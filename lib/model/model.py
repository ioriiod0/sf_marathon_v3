# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-01 14:45:35
# @Last Modified by:   ioriiod0
# @Last Modified time: 2017-11-07 22:37:57


import tensorflow as tf

def ACNet(_input, scope, args):
	with tf.variable_scope(scope):
		x = tf.layers.conv2d(_input,32,3,strides=(1, 1),activation=tf.nn.relu)
		x = tf.layers.conv2d(x,64,3,strides=(1, 1),activation=tf.nn.relu)
		x = tf.reshape(x.get_shape()[0],-1)

		policy = tf.layers.dense(x,args.hidden,activation=tf.nn.relu)
		policy = tf.layers.dense(policy,args.hidden,activation=tf.nn.relu)
		policy = tf.layers.dense(policy,args.action_dim,activation=tf.nn.softmax)

		value = tf.layers.dense(x,args.hidden,activation=tf.nn.relu)
		value = tf.layers.dense(value,args.hidden,activation=tf.nn.relu)
		value = tf.layers.dense(value,1)

	return policy,value


		