
import gevent
from gevent import monkey;monkey.patch_all()

from server import app
from server.logger import init_logger
init_logger('SERVER','DEBUG')

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5555)
