# -*- coding: utf-8 -*-
# @Author: ioriiod0
# @Date:   2017-11-07 17:50:07
# @Last Modified by:   ioriiod0
# @Last Modified time: 2017-11-07 17:50:20



import logging
import logging.handlers

def init_logger(name, level, f = None):
	LEVEL = getattr(logging, level.upper(), None)
	logger = logging.getLogger(name)
	logger.propagate = False #don't propagate to root logger!
	logger.setLevel(LEVEL)
	formatter = logging.Formatter('%(asctime)s - %(process)d - %(thread)d - %(name)s - %(levelname)s - %(message)s')

	if f:
		fh = logging.handlers.RotatingFileHandler(f, maxBytes=1024*1024*50, backupCount=5)
		fh.setLevel(LEVEL)
		fh.setFormatter(formatter)
		logger.addHandler(fh)
	else:
		sh = logging.StreamHandler()
		sh.setLevel(LEVEL)
		sh.setFormatter(formatter)
		logger.addHandler(sh)

	return logger