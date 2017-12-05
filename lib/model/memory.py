# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-03 11:07:06
# @Last Modified by:   ioriiod0
# @Last Modified time: 2017-11-07 17:30:09

import numpy as np

class Memory(object):
	"""docstring for Memory"""
	def __init__(self):
		super(Memory, self).__init__()
		self.index = 0
		self.mem = {
			"states": None,
			"target_actions": None,
			"target_vs": None,
			"advantages": None,
		}

	def put(self,experience):
		assert len(experience['states']) == len(experience['target_actions'])
		assert len(experience['target_actions']) == len(experience['target_vs'])
		assert len(experience['target_vs']) == len(experience['advantages'])
		for k,v in self.mem.iteritems():
			if not v:
				self.mem[k] = experience
			else:
				self.mem[k] = np.concatenate([v,experience[k]],axis=0)


	def sample(self,batch_size,shuffle=True):
		l = list(range(len(self.mem['states'])))
		if shuffle:
			np.random.shuffle(l)
			l = l[:batch_size]
		else:
			l = l[self.index:self.index+batch_size]
			self.index += batch_size
			if self.index > len(self.mem['states']):
				self.index = 0

		return {
			"states": self.mem["states"][l],
			"target_actions": self.mem["target_actions"][l],
			"target_vs": self.mem["target_vs"][l],
			"advantages": self.mem["advantages"][l],
		}
