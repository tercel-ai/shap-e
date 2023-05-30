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
            delete_file(d['file_image'])
            delete_file(d['file_3d'])

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

def get_records(force=False):
    if not webdata or force:
        load_records()
    return list(copy.deepcopy(webdata))


def get_record_by_key_val(key:str, val:str):
    global webdata
    if not webdata:
        load_records()

    i = -1
    res = None
    for index, item in enumerate(webdata):
        if item[key] == val:
            i = index
            res = item
            break

    if i > -1:
        del webdata[i]
        save_record(res)
    
    return copy.deepcopy(res)

def get_record_by_prompt(prompt:str):
    return get_record_by_key_val('prompt', prompt)


def get_record_by_image(filepath:str):
    return get_record_by_key_val('file_image', filepath)