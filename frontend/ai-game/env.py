# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-01 14:44:26
# @Last Modified by:   ioriiod0
# @Last Modified time: 2017-11-16 15:10:41

import sys
import numpy as np
import time
import random

class Env(object):
	"""docstring for Env"""
	def __init__(self,_id,owner,world_size,num_jobs,value_range,max_steps,rand):
		super(Env, self).__init__()
		self.world_size = world_size
		self.num_jobs = num_jobs
		self.max_steps = max_steps
		self.value_range = value_range
		self._id = _id
		self.owner = owner
		self.rand = rand
		self.benchmark = False

	def _gen_world(self):
		self.jobs = np.zeros((self.world_size,self.world_size))
		self.coord = (0,0)

	def _gen_wall(self):
		self.walls = np.zeros((self.world_size,self.world_size))
		self.wall_indexes = [(1,2),(2,3),(4,3),(4,4),(9,6),(8,6),
								(6,5),(6,8),(6,9),(3,9),(2,9),(2,10),(9,2),(8,2)]
		for x,y in self.wall_indexes:
			self.walls[x][y] = 1


	def _gen_job(self,n,gen_value):
		if n <= 0:
			return
		l = list(range(self.world_size*self.world_size))
		self.rand.shuffle(l)
		i = 0
		for xx in l:
			x = xx % self.world_size
			y = xx / self.world_size
			if self.jobs[x][y] != 0 or self.walls[x][y] != 0 or (x,y) == self.coord:
				continue
			self.jobs[x][y] = gen_value()
			i += 1
			if i == n:
				break


	def reset(self):
		self._gen_world()
		self._gen_wall()
		self._gen_job(self.num_jobs,lambda : self.rand.randint(*self.value_range))
		self.score = 0
		self.steps = 0
		self.replay = []
		self.timestamp = time.time()
		self.first_time = self.timestamp
		return self.get_state()


	def get_state(self):
		ai = {"x": self.coord[0],"y": self.coord[1]}
		walls = [ {"x":x,"y":y} for x,y in self.wall_indexes]
		jobs = []
		for x in range(self.world_size):
			for y in range(self.world_size):
				if self.jobs[x][y] > 0:
					jobs.append({
						"x":x,
						"y":y,
						"value":self.jobs[x][y],
					})
		ret = {
			"ai": ai,
			"walls": walls,
			"jobs": jobs,
			"score": self.score,
		}
		self.replay.append(ret)
		return ret

	def step(self,action):
		self.timestamp = time.time()
		self.steps += 1
		done = (self.steps == self.max_steps)
		if action in (0,"U"):
			x,y = self.coord[0]-1,self.coord[1]
		elif action in (1,"D"):
			x,y = self.coord[0]+1,self.coord[1]
		elif action in (2,"L"):
			x,y = self.coord[0],self.coord[1]-1
		elif action in (3,"R"):
			x,y = self.coord[0],self.coord[1]+1
		else:
			raise Exception("invalid action")

		self.jobs = np.clip(self.jobs - 1,0,float("inf"))
		valid = (0 <= x < self.world_size) and (0 <= y < self.world_size) and (self.walls[x][y] == 0)

		if not valid:
			reward = 0
		else:
			self.coord = (x,y)
			reward = self.jobs[x][y]
			if reward > 0:
				self.score += reward
			self.jobs[x][y] = 0

		existing = self.jobs[self.jobs > 0].size
		delta = self.num_jobs - existing:
		for i in range(delta):
			if self.rand.float() < 0.5:
				self._gen_job(2,lambda : self.rand.randint(*self.value_range))
		if done:
			self.duration = self.timestamp - self.first_time

		return self.get_state(),action,reward,done


	def render(self):
		for i in range(self.world_size):
			for j in range(self.world_size):
				if j == 0:
					sys.stdout.write("|")
				if self.jobs[i][j] > 0:
					sys.stdout.write("%02d|" % self.jobs[i][j])
				elif self.walls[i][j] > 0:
					sys.stdout.write("x |")
				elif self.coord == (i,j):
					sys.stdout.write("* |")
				else:
					sys.stdout.write("  |")
			sys.stdout.write("\r\n")


if __name__ == '__main__':
	env = Env("a","b",12,18,(18,36),288,random.Random(10))
	env.reset()
	env.render()
	while True:
		action = np.random.choice(["U","D","L","R"])
		print "coord before:", env.coord,"action:",action
		state,action,reward,done = env.step(action)
		print "coord after:", env.coord,"reward:",reward
		print "coord ai:",env.coord
		env.render()
		if done:
			break
		time.sleep(3)
	# env.step()
