# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-01 20:23:11
# @Last Modified by:   ioriiod0
# @Last Modified time: 2017-11-07 22:25:52

import threading
import Queue
import numpy as np
import tensorflow as tf
import logging
logger = logging.getLogger("APP.DPPO")
from util import *


class Worker(threading.Thread):
	"""docstring for DPPO"""
	def __init__(self, scope, sess, queue, cond, coord, env_creator, network_creator, args):
		super(DPPO, self).__init__()
		self.args = args
		self.scope = scope
		self.sess = sess
		self.env = env_creator(scope,args)
		self.queue = queue
		self.cond = cond
		self.coord = coord
	
		self.optimizer = tf.train.AdamOptimizer(args.lr)

		self.input = tf.placeholder(tf.float32,[None] + args.state_dim)
		self.advantages = tf.placeholder(tf.float32,[None],name='advantages')
		self.target_actions = tf.placeholder(tf.float32,[None,args.action_dim],name='target_actions')
		self.target_v = tf.placeholder(tf.float32,[None],name='target_v')

		self.policy,self.value = network_creator(self.input,scope,args)
		self.old_policy,self.old_value = network_creator(self.input,scope+"_old",args)
		self.update_local = [update_target_graph('chief',self.scope),update_target_graph('chief',self.scope+"_old")]

		def log_prob(policy,action):
			prob = policy * action
			prob = tf.reduce_sum(prob,axis=-1)
			return tf.log(prob)

		ratio = tf.exp(log_prob(self.policy,self.target_actions)-log_prob(self.old_policy,self.target_actions))
		surr1 = ratio * self.advantages
		surr2 = tf.clip_by_value(ratio,1.0 - args.clip_param,1.0 + args.clip_param) * self.advantages
		self.policy_loss = -tf.reduce_mean(tf.minimum(surr1,surr2))
		self.value_loss = tf.reduce_mean(tf.square(self.value-target_v))
		self.entrophy = -tf.reduce_mean(tf.log(policy) * policy)
		self.loss = policy_loss + args.coef_value * value_loss - args.coef_entropy * entrophy

		local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope)
		grads = tf.gradients(loss, local_vars)
		self.grads, self.grad_norms = tf.clip_by_global_norm(grads,args.grad_clip)


	def preprocessing(self,experience,bootstrap=0):
		#state,action,reward,value,done
		experience = np.array(experience)
		values = experience[:,3]
		rewards = experience[:,2]
		target_vs = discount(reward,self.args.gamma,bootstrap)
		values.append(bootstrap)
		advantages = reward + self.gamma * values[1:] - values[:-1]
		advantages = discount(advantages,self.args.gae_gamma * self.args.gamma)

		return {
			"states": experience[:,0],
			"target_actions": experience[:,1],
			"target_vs": target_vs,
			"advantages": advantages
		}	


	def train(self,experience,epoch):
		feed_dict = {
			self.input: experience['input'],
			self.advantages: experience['advantages'],
			self.target_actions : experience['target_actions'],
			self.target_v: experience['target_v'],
		}
		
		loss,policy_loss,value_loss,entropy,grad_norms,grads = self.sess.run([self.loss,self.policy_loss,self.value_loss,self.entrophy,self.grad_norms,self.grads],feed_dict=feed_dict)
		logger.info("======================> epoch:%s,loss:%s,policy_loss:%s,value_loss:%s,entropy:%s",epoch,loss,policy_loss,value_loss,entropy)
		summary = tf.Summary()
		summary.value.add(tag='loss', simple_value=float(loss))
		summary.value.add(tag='policy_loss', simple_value=float(policy_loss))
		summary.value.add(tag='value_loss', simple_value=float(value_loss))
		summary.value.add(tag='entropy', simple_value=float(entropy))
		summary.value.add(tag='grad_norms', simple_value=float(grad_norms))
		self.summary_writer.add_summary(summary, epoch)
		self.summary_writer.flush()

	
	def infer(self):
		buf = []
		state = env.reset()
		while True:
			policy,value = self.sess.run([self.policy,self.value],feed_dict={
				self.input: state
			})
			new_state,action,reward,done = env.step(policy)
			buf.append((state,action,reward,value,done))
			state = new_state

			if done:
				experience = self.preprocessing(buf,0)
				yield experience
				buf = []
				state = env.reset()

			if len(buf) == self.args.batch_size:
				_,value = self.sess.run([self.policy,self.value],feed_dict={
					self.input: state
				})
				experience = self.preprocessing(buf,value)
				yield experience
				buf = []


	def run(self):
		with self.sess.as_default(), self.sess.graph.as_default(): 
			while not self.coord.should_stop():
				self.sess.run(self.update_local)
				for i,batch in enumerate(self.infer()):
					grads = self.train(batch)
					self.quque.put(grads)
					if i == args.M:
						break

				with self.cond:
					self.cond.wait()


			

class Chief(threading.Tread):
	"""docstring for Chief"""
	def __init__(self, sess, queue, cond, coord, env_creator, network_creator, args):
		super(Chief, self).__init__()
		self.args = args
		self.sess = sess
		self.queue = queue
		self.cond = cond
		self.coord = coord

		self.optimizer = tf.train.AdamOptimizer(args.lr)
		self.env = env_creator("chief",args)
		self.input = tf.placeholder(tf.float32,[None] + args.state_dim)
		self.policy,self.value = network_creator(self.input,"chief",args)

		self.trainable_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "chief")
		self.grads_input = [ tf.placeholder(tf.float32,[None] + var.get_shape.as_list()) for var in self.trainable_vars]
		self.grads = tf.reduce_mean(self.grads_input,axis=0)
		self.apply_gradients = self.optimizer.apply_gradients(zip(grads,trainable_vars))

		self.saver = tf.train.Saver(self.trainable_vars,max_to_keep=5)
		if args.load_model:
			ckpt = tf.train.get_checkpoint_state(args.model_path)
			self.saver.restore(sess,ckpt.model_checkpoint_path)
		else:
			self.sess.run(tf.global_variables_initializer())
			self.saver = tf.train.Saver(max_to_keep=5)


	def test(self):
		state = env.reset()
		total_reward = 0
		while True:
			policy,value = self.sess.run([self.policy,self.value],feed_dict={
				self.input: state
			})
			state,action,reward,done = env.step(policy,greedy=True)
			total_reward += reward
			if done:
				break

		return total_reward
		
			
	def run(self):
		with self.sess.as_default(), self.sess.graph.as_default(): 
			grads = []
			for epoch in range(self.args.epochs):
				for j in range(self.args.num_workers*self.args.M):
					g = self.queue.get()
					grads.extend(g)
				self.sess.run(self.apply_gradients,{self.grads_input:grads})

				with self.cond:
					self.cond.notifyAll()

				if i % 1000 == 0:
					self.saver.save(self.sess,"%s/epochs_%d" % (self.master.model_path,epoch))

				if i % 100 == 0:
					total_reward = self.test()
					logger.info("=================> chief <============== epoch:%s,total_reward:%s",epoch,total_reward)

		self.coord.request_stop()


class DPPO(object):
	"""docstring for DPPO"""
	def __init__(self, sess, env_creator, network_creator, args):
		super(DPPO, self).__init__()
		self.args = args
		self.sess = sess

		queue = Queue.Queue()
		coord = tf.train.Coordinator()
		cond = threading.Condition()

		self.chief = Chief(sess,self.queue,self.cond,self.coord,env_creator,network_creator,args)
		self.workers = []
		for i in range(args.num_workers):
			w = Worker("worker_%d" % i,sess,self.queue,self.cond,self,coord,env_creator,network_creator,args)
			self.workers.append(w)


	def run(self):
		self.chief.start()
		for w in self.workers:
			w.start()

		self.chief.join()
		for w in self.workers:
			w.join()






		







		


			


		


				







