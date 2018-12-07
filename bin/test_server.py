import asyncio
import sys
from sanic import Sanic
from sanic import response
import time
import random


app = Sanic(__name__)


@app.route('/start',methods=["POST"])
async def on_start(request):
	json = request.json
	print (json)
	return response.json({})

@app.route('/step',methods=["POST"])
async def on_step(request):
	json = request.json
	# await asyncio.sleep(3)
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


