import requests
import numpy as np
import gevent
import json
from gevent import monkey;monkey.patch_all()
import time

ENV = "competition"
ENV_URL = '/%s'
STEP = '/%s/%s/move'
REPLAY_URL = '/replays/%s'

def run_test(n):
    name = "user%s" % n
    for i in range(10):
        print "user",name,"round",i
        print ENV_URL % ENV
        res = requests.post(ENV_URL % ENV,data=json.dumps({"name":name}))
        assert res.status_code == 200
        data = res.json()
        print data
        _id = data['id']

        for j in range(400):
            act = np.random.choice(['U','D','L','R'])
            res = requests.post(STEP % (ENV,_id),data=json.dumps({"direction":act}))
            # print STEP % (ENV,_id)
            assert res.status_code == 200

def get_billboard():
    res = requests.get(ENV_URL % ENV)
    assert res.status_code == 200
    data = res.json()

    for x in data['data']:
        print x


def get_replay(_id):
    res = requests.get(REPLAY_URL % _id)
    assert res.status_code == 200
    data = res.json()['replay']
    for x in data:
        print x


if __name__ == '__main__':
    gs = []
    for i in range(2):
        g = gevent.spawn(run_test,i)
        gs.append(g)

    gevent.wait(gs)
    get_billboard()

    # get_replay("04f6d10a-d6dc-4e65-84e4-98ea4019d040")
