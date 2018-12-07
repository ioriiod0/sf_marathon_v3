import os
import random
import json
from uuid import uuid4

from env.env import *
from server import app
from server.errors import *



class Model(object):
	def __init__(self):
		self.envs = {}
		os.system("mkdir -p %s" % app.config['REPLAY_DIR'])

	def save_replay(self,env):
		config = app.config
		path = "%s/%s" % (config['REPLAY_DIR'],env.name)
		with open(path,'w') as f:
			json.dump(env.replay,f)

	def load_replay(self,name):
		config = app.config
		path = "%s/%s" % (config['REPLAY_DIR'],name)
		with open(path) as f:
			return json.load(f)


	def create_env(self,name,p1,p2,seed=None):
		config = app.config
		if name in self.envs:
			raise Forbidden("name already existed")

		if seed:
			rand = random.Random(seed)
		else:
			rand = random.Random(int(time.time()))

		env = Env(name,p1,p2,config['ENV_CONF'],rand)
		self.envs[name] = env
		return env

	def stop_env(self,name):
		env = self.envs.get(name)
		if env is None:
			return
		env.stopped = True

	def del_env(self,name):
		env = self.envs.get(name)
		if env is None:
			return
		if env.done or env.stopped:
			del self.envs[name]
		else:
			raise Forbidden("env is still running...")

	def get_envs(self):
		r = []
		for name,env in self.envs.items():
			r.append({
				'name': env.name,
				'player1': {
					'name':env.player1.name,
					'socre':env.player1.score,
				},
				'player2': {
					'name':env.player2.name,
					'socre':env.player2.score,
				},
				'steps': env.steps,
				'done': env.done,
				'stopped': env.stopped,
				'create_at': env.create_at,
			})
			
		r = sorted(r,key=lambda x:x['create_at'],reverse=True)
		return r


	def get_replay(self,_id):
		replay = self.load_replay(_id)
		return replay


m = Model()
