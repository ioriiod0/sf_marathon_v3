# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-01 14:44:26
# @Last modified by:   ioriiod0
# @Last modified time: 2017-12-05T16:30:55+08:00

import sys
import time
import random
import copy
import numpy as np


class Player(object):
	def __init__(self,name,home,n_jobs,value,score):
		super(Player,self).__init__()
		self.name = name
		self.x = home[0]
		self.y = home[1]
		self.home_x = home[0]
		self.home_y = home[1]
		self.n_jobs = n_jobs
		self.value = value
		self.score = score

	def reset(self):
		self.x = self.home_x
		self.y = self.home_y
		self.n_jobs = 0
		self.value = 0
		self.score = 0

	def __str__(self):
		return str(self.__dict__)
		
	__repr__ = __str__

class Env(object):
	"""docstring for Env"""
	def __init__(self,name,p1_name,p2_name,conf,rand):
		super(Env, self).__init__()
		self.conf = conf
		self.name = name
		self.rand = rand
		self.stopped = False
		self.done = False
		self.create_at = time.time()
		self.score = 0
		self.steps = 0
		self.replay = []

		self.player1 = Player(p1_name,self.conf['player1_home'],0,0,0)
		self.player2 = Player(p2_name,self.conf['player2_home'],0,0,0)
		self.current_player = self.player1



	def _gen_world(self):
		world_size = self.conf['world_size']
		self.jobs = np.zeros((world_size,world_size))

	def _gen_wall(self):
		world_size = self.conf['world_size']
		num_walls = self.conf['num_walls']
		self.walls = np.zeros((world_size,world_size))
		l = list(range(world_size*world_size))
		self.rand.shuffle(l)
		
		i = 0
		for xx in l:
			x = xx // world_size
			y = xx % world_size
			if (x,y) in ((self.player1.x,self.player1.y),(self.player2.x,self.player2.y),(self.player1.home_x,self.player1.home_y),(self.player2.home_x,self.player2.home_y)):
				continue
			self.walls[x][y] = 1
			i += 1
			if i == num_walls:
				break


	def _gen_job(self,n,gen_value):
		if n <= 0:
			return
		world_size = self.conf['world_size']

		l = list(range(world_size*world_size))
		self.rand.shuffle(l)

		i = 0
		for xx in l:
			x = xx // world_size
			y = xx % world_size
			if self.jobs[x][y] != 0 or self.walls[x][y] != 0 or (x,y) in ((self.player1.x,self.player1.y),(self.player2.x,self.player2.y),(self.player1.home_x,self.player1.home_y),(self.player2.home_x,self.player2.home_y)):
				continue
			v = gen_value()
			self.jobs[x][y] = v
			i += 1
			self.score_gened += v
			if i == n:
				break


	def reset(self):
		self.score_gened = 0
		self._gen_world()
		self._gen_wall()
		self._gen_job(self.conf['num_jobs'],lambda : self.rand.randint(*self.conf['value_range']))
		self.stopped = False
		self.done = False
		self.score = 0
		self.steps = 0
		self.replay = []
		self.player1.reset()
		self.player2.reset()
		self.current_player = self.player1
		return self.get_state()


	def get_state(self):
		world_size = self.conf['world_size']
		p1 = self.player1
		p2 = self.player2
		player1 = copy.deepcopy(p1.__dict__)
		player2 = copy.deepcopy(p2.__dict__)

		walls = []
		jobs = []
		for x in range(world_size):
			for y in range(world_size):
				if self.jobs[x][y] > 0:
					jobs.append({
						"x":x,
						"y":y,
						"value":self.jobs[x][y],
					})

				if self.walls[x][y] > 0:
					walls.append({"x":x,"y":y})

		ret = {
			"player1": player1,
			"player2": player2,
			"walls": walls,
			"jobs": jobs,
		}
		self.replay.append(ret)
		return ret

	def _move(self,action):
		p = self.current_player
		o = self.player1 if self.current_player is self.player2 else self.player2

		world_size = self.conf['world_size']

		if action in (0,"U"):
			x,y = p.x-1,p.y
		elif action in (1,"D"):
			x,y = p.x+1,p.y
		elif action in (2,"L"):
			x,y = p.x,p.y-1
		elif action in (3,"R"):
			x,y = p.x,p.y+1
		else: #stay..
			x,y = p.x,p.y

		valid = (0 <= x < world_size) and (0 <= y < world_size) and (self.walls[x][y] == 0) and (x,y) != (o.home_x,o.home_y)

		if valid:
			p.x = x
			p.y = y

		return p

	def _pickup(self):
		p = self.current_player
		if self.jobs[p.x][p.y] > 0 and p.n_jobs < self.conf['capacity']:
			p.n_jobs += 1
			p.value += self.jobs[p.x][p.y]
			self.jobs[p.x][p.y] = 0
	
	def _delivery(self):
		p = self.current_player
		if (p.x,p.y) == (p.home_x,p.home_y):
			p.n_jobs = 0
			p.score += p.value
			p.value = 0

	def _switch_player(self):
		if self.current_player is self.player1:
			self.current_player = self.player2
		elif self.current_player is self.player2:
			self.current_player = self.player1
		else:
			raise Exception("should not happened!!")
		
	def step(self,p_name,action):
		assert self.current_player.name == p_name
		
		self._move(action)
		self._pickup()
		self._delivery()
		self._switch_player()
		self.steps += 1

		self.done = done = (self.steps == self.conf['max_steps']*2)
		existing = self.jobs[self.jobs > 0].size
		delta = self.conf['num_jobs'] - existing
		self._gen_job(delta,lambda : self.rand.randint(*self.conf['value_range']))

		return self.get_state()


	def render(self):
		world_size = self.conf['world_size']
		for i in range(world_size):
			for j in range(world_size):
				if j == 0:
					sys.stdout.write("|")
				if self.jobs[i][j] > 0:
					sys.stdout.write("%02d|" % self.jobs[i][j])
				elif self.walls[i][j] > 0:
					sys.stdout.write("x |")
				elif (self.player1.x,self.player1.y) == (i,j):
					sys.stdout.write("* |")
				elif (self.player2.x,self.player2.y) == (i,j):
					sys.stdout.write("@ |")
				elif (self.player1.home_x,self.player1.home_y) == (i,j):
					sys.stdout.write("H |")
				elif (self.player2.home_x,self.player2.home_y) == (i,j):
					sys.stdout.write("M |")
				else:
					sys.stdout.write("  |")
			sys.stdout.write("\r\n")
		print ('================')


if __name__ == '__main__':
	conf = {
		'world_size': 12,
		'capacity': 10,
		'player1_home': (5,5),
		'player2_home': (6,6),
		'num_walls': 24,
		'num_jobs': 24,
		'value_range': (6,12),
		'max_steps': 200
	}
	# p1_actions = ['D','D','L','R','U','L','L','U']
	# p2_actions = ['D','D','U','R','L','R','U','D','D']
	p1_actions = ['D','R','R','D','R','D','D','D']
	p2_actions = ['S','U','U','L','U','U']
	env = Env("","p1","p2",conf,random.Random(20))
	env.reset()
	env.render()
	while True:
		if p1_actions:
			action1 = p1_actions[0] #np.random.choice(["U","D","L","R"])
			p1_actions = p1_actions[1:]
		else:
			action1 = 'S'

		if p2_actions:
			action2 = p2_actions[0] #np.random.choice(["U","D","L","R"])
			p2_actions = p2_actions[1:]
		else:
			action2 = 'S'
		# action2 = 'S'#np.random.choice(["U","D","L","R"])
		print ('P1:',action1)
		state = env.step("p1",action1)
		env.render()
		print ('P2:',action2)
		state = env.step("p2",action2)
		env.render()

		print ("coord after:", env.player1,env.player2)
		print ("coord ai:",env.player1,env.player2)
		
		if env.done:
			break
		time.sleep(0.1)
	# env.step()
