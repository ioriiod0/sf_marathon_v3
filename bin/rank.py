
import requests
import numpy as np
import gevent
import json
from gevent import monkey;monkey.patch_all()
import time

ENV = "competition"
ENV_URL = ':4444/%s'
# STEP = ':5555/%s/%s/move'
# REPLAY_URL = ':5555/replays/%s'

def get_billboard():
    res = requests.get(ENV_URL % ENV)
    assert res.status_code == 200
    data = res.json()
    data = data['data']
    with open("result2.json",'w') as f:
        json.dump(data,f)

if __name__ == '__main__':
    get_billboard()

    # get_replay("04f6d10a-d6dc-4e65-84e4-98ea4019d040")
