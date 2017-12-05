# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-07 14:42:42
# @Last Modified by:   ioriiod0
# @Last Modified time: 2017-11-07 22:32:26

import numpy as np
import tensorflow as tf


def discount(rs,gamma,boostrap=0):
	vs = []
	v = boostrap
	for r in rs[::-1]:
		v = r + gamma * v
		vs.append(v)
	vs.reverse()
	return np.array(vs)


def update_target_graph(from_scope,to_scope):
	from_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, from_scope)
	to_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, to_scope)

	op_holder = []
	for from_var,to_var in zip(from_vars,to_vars):
		op_holder.append(to_var.assign(from_var))
	return op_holder