
import os
import time
import json
from functools import wraps
from flask import request,redirect,session,g,Response,json,g
from schema import Schema, And, Use, Optional, SchemaError,Optional
from flask_sockets import Sockets

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
		def decorated_function(*args, **kwargs):
			try:

				if schema and request.data is not None:
					g.json = json.loads(request.data)
					schema.validate(g.json)
				data,code = f(*args, **kwargs)
				# logger.debug("data:%s" % data)
				res = Response(json.dumps(data),status=code,mimetype='application/json')
				return res
			except (BadRequest,SchemaError),e:
				logger.error(e,exc_info=True)
				return Response(json.dumps({ "msg":str(e)}),status=400,mimetype='application/json')
			except Unauthorized,e:
				logger.error(e,exc_info=True)
				return Response(json.dumps({ "msg":str(e)}),status=401,mimetype='application/json')
			except Forbidden,e:
				logger.error(e,exc_info=True)
				return Response(json.dumps({ "msg":str(e)}),status=403,mimetype='application/json')
			except NotFound,e:
				logger.error(e,exc_info=True)
				return Response(json.dumps({ "msg":str(e)}),status=404,mimetype='application/json')
			except Exception,e:
				logger.error(e,exc_info=True)
				return Response(json.dumps({ "msg":str(e)}),status=500,mimetype='application/json')
		return decorated_function
	return _


# @app.route("/test",methods=["POST"])
# @json_api()
# def create_test():
#     _id,state = m.create_env()
#     logger.info("create env,id:%s",_id)
#     return {"msg":"OK","id":_id,"state":state},200

@app.route("/competition",methods=["POST"])
@json_api({'name':basestring})
def create_competition():
    data = g.json
    _id,state = m.create_env(data.get("name"))
    logger.info("create env,id:%s",_id)
    return {"msg":"OK","id":_id,"state":state},200

@app.route("/benchmark",methods=["POST"])
@json_api({'name':basestring})
def create_benchmark():
    data = g.json
    _id,state = m.create_benchmark(data['name'])
    logger.info("create benchmark,id:%s",_id)
    return {"msg":"OK","id":_id,"state":state},200


# @app.route("/test/<_id>/move",methods=["POST"])
@app.route("/competition/<_id>/move",methods=["POST"])
@app.route("/benchmark/<_id>/move",methods=["POST"])
@json_api({'direction': lambda x: x in ['U','D','L','R']})
def step(_id):
    state,action,reward,done = m.step(_id,g.json['direction'])
    return {"msg":"OK","id":_id,"state":state,"action":action,"reward":reward,"done":done},200


@app.route("/competition",methods=["GET"])
@json_api()
def get_billboard():
    b = m.get_billboard()
    return {"msg":"OK","data":b},200


@app.route("/benchmark",methods=["GET"])
@json_api()
def get_benchmark():
    b = m.get_benchmark()
    return {"msg":"OK","data":b},200


@app.route("/test/replays/<_id>",methods=["GET"])
@app.route("/competition/replays/<_id>",methods=["GET"])
@app.route("/benchmark/replays/<_id>",methods=["GET"])
@json_api()
def get_replay(_id):
    replay = m.get_replay(_id)
    return {"msg":"OK","replay":replay},200
