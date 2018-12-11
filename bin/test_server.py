import asyncio
import sys
from sanic import Sanic
from sanic import response
import time
import random


app = Sanic(__name__)

"""
/start 用于比赛服务器通知参赛AI比赛开始
	输入:
		格式为JSON
		{}
	输出: 
		HTTP_CODE 必须为200， 表示就绪

	当参赛双方都就绪时，比赛才会正式开始
/step 输入：当前地图状态，输出：AI决策出的动作
/end 用于比赛服务器通知参赛AI比赛结束

"""

@app.route('/start',methods=["POST"])
async def on_start(request):
	json = request.json
	print (json)
	return response.json({})

@app.route('/step',methods=["POST"])
async def on_step(request):
	json = request.json
	await asyncio.sleep(0.1)
	print (json)
	return response.json({'action':random.choice(['U','D','L','R'])})

@app.route('/end',methods=["POST"])
async def on_end(request):
	json = request.json
	print (json)
	return response.json({})

def main():
	seed = int(sys.argv[1])
	random.seed(seed)
	app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
	main()


