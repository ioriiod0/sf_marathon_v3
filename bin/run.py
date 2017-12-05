# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-07 17:50:30
# @Last Modified by:   ioriiod0
# @Last Modified time: 2017-11-08 15:05:53


import argparse
import os

import tensorflow as tf
from env.env import *
from model.dppo import *
from model.memory import *
from model.logger import *
from model.model import *

init_logger("APP","DEBUG")
import logging
logger = logging.getLogger("APP")

def parse_array(s):
	return map(int,s.split(","))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='RL train.')
	parser.add_argument('--epochs', dest='epochs', help='max_epochs',default=1000,type=int)
	parser.add_argument('--log_path', dest='log_path', help='log_path',default="/log")
	parser.add_argument('--lr', dest='lr', help='learning rate',default=0.001,type=float)
	parser.add_argument('--grad_clip', dest='grad_clip', help='grad_clip',default=100.0,type=float)
	parser.add_argument('--gamma', dest='gamma', help='gamma',default=0.99,type=float)
	parser.add_argument('--gae_gamma', dest='gae_gamma', help='gae_gamma',default=0.96,type=float)
	parser.add_argument('--hidden', dest='hidden', help='hidden',default=256,type=int)
	parser.add_argument('--model_path', dest='model_path', help='model_path',default="/model")
	parser.add_argument('--load_model', dest='load_model',default=False, help='load_model',action='store_true')
	parser.add_argument('--num_workers', dest='num_workers', help='num_workers',type=int,default=4)
	parser.add_argument('--coef_entropy', dest='coef_entropy', help='coef_entropy', type=float, default=0.0)
	parser.add_argument('--coef_value', dest='coef_value', help='coef_value', type=float, default=0.5)
	parser.add_argument('--state_dim', dest='state_dim', help='state_dim')
	parser.add_argument('--action_dim', dest='action_dim', help='action_dim', type=int)


	args = parser.parse_args()
	args.state_dim = parse_args(args.state_dim)

	def env_creator(scope,args):
		return Env(world_size,gen_job_speed,init_job_value,max_steps,init_jobs)

	with tf.Session() as sess:
		dppo = DPPO(sess, env_creator, ACNet, args)
		dppo.run()






