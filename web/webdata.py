import json
import copy
import os
from datetime import datetime, timezone
from collections import deque
from entry import delete_file

max_records = int(os.environ.get('SHAPE_WEBDATA_MAX', 50))

webdata = deque([]);


class WebDataExcepiton(Exception):
    pass

def now_utc_str():
    utc_time = datetime.now(timezone.utc)
    return utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def save_record(data:dict):
    data['created_at'] = now_utc_str()
    global webdata
    try:
        if len(webdata) > max_records:
            d = webdata.pop()
            delete_file(d['image'])
            delete_file(d['3dfile'])

        webdata.appendleft(data)
        json_str = json.dumps(list(webdata))
        with open('.webdata.json', 'w') as f:
            f.write(json_str)
    except Exception as e:
        raise WebDataExcepiton(str(e))


def load_records():
    global webdata
    try:
        with open('.webdata.json', 'r') as f:
            json_str = f.read()
        webdata = deque(json.loads(json_str))
    except Exception as e:
        json_str = json.dumps([])
        with open('.webdata.json', 'w') as f:
            f.write(json_str)

def get_records():
    if not webdata:
        load_records()
    return list(webdata)