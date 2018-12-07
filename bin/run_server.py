# @Author: ioriiod0
# @Date:   2017-11-26T16:20:50+08:00
# @Last modified by:   ioriiod0
# @Last modified time: 2017-12-05T16:26:22+08:00



from server import app
from server.logger import init_logger
init_logger('SERVER','DEBUG')

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5555)
