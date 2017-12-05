import os
import random
import json
from uuid import uuid4

import gevent

from env.env import *
from server import app
from server.errors import *



class Model(object):
    def __init__(self):
        self.teams = {}
        self.envs = {}
        self.counts = {}
        self.benchmark = {}
        os.system("mkdir -p %s" % app.config['REPLAY_DIR'])
        self.start_gc()

    def start_gc(self):
        config = app.config
        def f():
            while True:
                t = time.time()
                to_remove = []
                for _id,env in self.envs.iteritems():
                    du = t - env.timestamp
                    # print t,env.timestamp,du,config['TIME_OUT']
                    if du > config['TIME_OUT']*2:
                        to_remove.append(env._id)

                for _id in to_remove:
                    env = self.envs[_id]
                    duration = time.time() - env.first_time
                    if env.owner:
                        print "timeout!!"
                        envs = self.teams[env.owner]
                        envs.append({
                            "id": env._id,
                            "score": env.score,
                            "duration": duration,
                            "score_gened": env.score_gened,
                        })
                        self.teams[env.owner] = envs

                    del self.envs[_id]
                time.sleep(1)
        gevent.spawn(f)

    def _save_replay(self,env):
        config = app.config
        path = "%s/%s" % (config['REPLAY_DIR'],env._id)
        with open(path,'w') as f:
            json.dump(env.replay,f)

    def _load_replay(self,_id):
        config = app.config
        path = "%s/%s" % (config['REPLAY_DIR'],_id)
        with open(path) as f:
            return json.load(f)


    def create_env(self,name=None):
        _id = str(uuid4())
        config = app.config

        if name not in self.teams:
            self.teams[name] = []
            self.counts[name] = 0

        self.counts[name] += 1
        env = Env(_id,name,config['WORLD_SIZE'],config['NUM_JOBS'],
            config['VALUE_RANGE'],config['MAX_STEPS'],random.Random())
        self.envs[_id] = env
        return _id,env.reset()


    def create_benchmark(self,name):
        _id = str(uuid4())
        config = app.config
        if name not in self.benchmark:
            b = {
                "count": 0,
                "envs": []
            }
            self.benchmark[name] = b

        b = self.benchmark[name]

        if b['count'] >= 10:
            raise Forbidden("only allowed benchmark 10 times")

        seed = config['SEED'] + b['count']
        b['count'] += 1

        env = Env(_id,name,config['WORLD_SIZE'],config['NUM_JOBS'],
                    config['VALUE_RANGE'],config['MAX_STEPS'],random.Random(seed))
        env.benchmark = True

        self.envs[_id] = env
        return _id,env.reset()


    def step(self,_id,action):
        config = app.config
        if _id not in self.envs:
            raise NotFound('env not found: %s' % _id)
        env = self.envs[_id]
        t = time.time()
        # if t - env.timestamp > config['TIME_OUT']:
        #     del self.envs[_id]
        #     raise NotFound('env timeout: %s' % _id)

        state,action,reward,done = env.step(action)

        if done:
            self._save_replay(env)
            # if t - env.first_time > 2.5 * 400:
            #     raise NotFound('env timeout: %s' % _id)

            del self.envs[_id]

            if env.benchmark:
                b = self.benchmark[env.owner]
                b['envs'].append({
                    "id": env._id,
                    "score": env.score,
                    "duration": env.duration,
                    "score_gened": env.score_gened,
                })

            elif env.owner:
                envs = self.teams[env.owner]
                envs.append({
                    "id": env._id,
                    "score": env.score,
                    "duration": env.duration,
                    "score_gened": env.score_gened,
                })
                self.teams[env.owner] = envs

        return state,action,reward,done


    def get_billboard(self):
        billboard = []
        for name,envs in self.teams.iteritems():
            if len(envs) == 0:
                continue
            avg = sum( env['score'] for env in envs ) / float(len(envs))
            avg_duration = sum( env['duration'] for env in envs ) / float(len(envs))
            billboard.append({
                "name": name,
                "avg_score": avg,
                "count": self.counts[name],
                "avg_duration": avg_duration,
                "envs": envs,
            })
        billboard = sorted(billboard,key=lambda x:x['avg_score'],reverse=True)
        return billboard


    def get_benchmark(self):
        benchmark = []
        for name,b in self.benchmark.iteritems():
            if len(envs) == 0:
                continue
            envs = b['envs']
            avg = sum( env['score'] for env in envs ) / float(len(envs))
            avg_duration = sum( env['duration'] for env in envs ) / float(len(envs))
            benchmark.append({
                "name": name,
                "count": self.counts[name],
                "avg_score": avg,
                "avg_duration": avg_duration,
                "envs": envs,
            })

        benchmark = sorted(benchmark[:10],key=lambda x:x['avg_score'],reverse=True)
        return benchmark

    def get_replay(self,_id):
        replay = self._load_replay(_id)
        return replay


m = Model()
