
import os
import time
import json
from functools import wraps
from sanic import response
import aiohttp
import asyncio
from asyncio import TimeoutError
from schema import Schema, And, Use, Optional, SchemaError

from server import app
from server.errors import *
from server.models import *

import logging
logger = logging.getLogger("SERVER.VIEWS")

def json_api(schema=None):
	if schema:
		schema = Schema(schema)
	def _(f):
		@wraps(f)
		async def decorated_function(request,*args, **kwargs):
			try:
				if schema:
					schema.validate(request.json)
				data,code = await f(request,*args, **kwargs)
				# logger.debug("data:%s" % data)
				return response.json({ "msg":"ok","result":data,"success":True},status=200)
				
			except (BadRequest,SchemaError) as e:
				logger.error(e,exc_info=True)
				return response.json({ "msg":str(e),"success":False},status=400)
			except Unauthorized as e:
				logger.error(e,exc_info=True)
				return response.json({ "msg":str(e),"success":False},status=401)
			except Forbidden as e:
				logger.error(e,exc_info=True)
				return response.json({ "msg":str(e),"success":False},status=403)
			except NotFound as e:
				logger.error(e,exc_info=True)
				return response.json({ "msg":str(e),"success":False},status=404)
			except Exception as e:
				logger.error(e,exc_info=True)
				return response.json({ "msg":str(e),"success":False},status=500)
		return decorated_function
	return _


async def post_json(session,url,data,timeout):
	resp = await session.post(url,json=data,timeout=timeout)
	ret = await resp.json()
	return ret,resp.status

async def get_action(session,url,state,timeout):
	try:
		ret,status = await post_json(session,url,state,timeout)
		if status != 200:
			x = 'S' #should stay.
		else:
			x = ret['action']
		return x
	except Exception as e:
		logger.error(e,exc_info=True)
		return 'S' #should stay.

@app.route("/competitions",methods=["POST"])
@json_api({
	'name':str,
	'player1':str,
	'player2':str,
	'player1_host':str,
	'player2_host':str,
	Optional('seed'):int
})
async def create_competition(request):
	data = request.json
	conf = app.config['ENV_CONF']

	player1 = data['player1']
	player2 = data['player2']
	player1_host = data['player1_host']
	player2_host = data['player2_host']
	env = m.create_env(data['name'],player1,player2,data.get('seed'))
	

	async def start(session):
		timeout = aiohttp.ClientTimeout(total=app.config['TIMEOUT']*3)
		for i in range(app.config['RETRY']):
			f1 = post_json(session,player1_host+"/start",{'name':env.name},timeout=timeout)
			f2 = post_json(session,player2_host+"/start",{'name':env.name},timeout=timeout)
			ready = True

			ret = await asyncio.gather(f1,f2,return_exceptions=True)
			logger.debug("gather:%s",ret)
			for x in ret:
				# logger.debug("x:::%s",x)
				if isinstance(x,Exception) or x[1] != 200:
					logger.error(x)
					ready = False
			
			if env.stopped:
				break

			if ready:
				return ready
		
		return False

	async def steps(session):
		state = env.reset()
		timeout = aiohttp.ClientTimeout(total=app.config['TIMEOUT'])
		while not (env.stopped or env.done):
			a1 = await get_action(session,player1_host+"/step",state,timeout=timeout)
			state = env.step(player1,a1)

			a2 = await get_action(session,player2_host+"/step",state,timeout=timeout)
			state = env.step(player2,a2)
	
			# p1,p2 = await asyncio.gather(f1, f2,return_exceptions=True)
			# state = env.step({player1:a1,player2:a2})

		return state


	async def end(session,state):
		timeout = aiohttp.ClientTimeout(total=app.config['TIMEOUT']*3)
		f1 = post_json(session,player1_host+"/end",state,timeout=timeout)
		f2 = post_json(session,player2_host+"/end",state,timeout=timeout)
		await asyncio.gather(f1, f2,return_exceptions=True)

	async def run():
		try:
			async with aiohttp.ClientSession() as session:
				ok = await start(session)
				if not ok:
					env.stopped = True
					return

				last_state = await steps(session)
				if not env.done:
					return

				m.save_replay(env)
				await end(session,last_state)
		
		except Exception as e:
			logger.error(e,exc_info=True)
			env.stopped = True

	app.add_task(run())
	return {"name":env.name},200


@app.route("/competitions",methods=["GET"])
@json_api()
async def get_competitions(request):
	envs = m.get_envs()
	return {"competitions":envs},200



@app.route("/competitions/<name>/replay",methods=["GET"])
@json_api()
async def get_replay(request,name):
	replay = m.get_replay(name)
	return {"name":name,"replay":replay},200


@app.route("/competitions/<name>/stop",methods=["POST"])
@json_api()
async def stop_competition(request,name):
	m.stop_env(name)
	return {"name":name},200


@app.route("/competitions/<name>",methods=["DELETE"])
@json_api()
async def delete_competition(request,name):
	m.del_env(name)
	return {"name":name},200

