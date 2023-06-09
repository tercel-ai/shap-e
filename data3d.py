import json
import copy
import os
import hashlib
from datetime import datetime, timezone
from collections import deque

max_records = int(os.environ.get('SHAPE_DATA3D_MAX', 50))

data3d = deque([]);


class Data3DExcepiton(Exception):
    pass

def now_utc_str():
    utc_time = datetime.now(timezone.utc)
    return utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def md5(val: str):
    m = hashlib.md5()
    m.update(val.encode('utf-8'))
    return m.hexdigest()

def delete_file(filepath):
    try:
        os.remove(filepath)
        return True
    except OSError as e:
        return False
    
def save(_data3d: list):
    try:
        json_str = json.dumps(_data3d)
        with open('.data3d.json', 'w') as f:
            f.write(json_str)
    except Exception as e:
        raise Data3DExcepiton(str(e))
    
def add_record(data:dict):
    data['created_at'] = now_utc_str()
    global data3d
    data3d = load_records()
    try:
        if len(data3d) > max_records:
            d = data3d.pop()
            delete_file(d['file_image'])
            delete_file(d['file_3d'])

        data3d.appendleft(data)
        save(list(data3d))
    except Exception as e:
        raise Data3DExcepiton(str(e))


def load_records(force=False):
    global data3d
    try:
        with open('.data3d.json', 'r') as f:
            json_str = f.read()
        data3d = deque(json.loads(json_str))
    except Exception as e:
        if force:
            data3d = []
            save(data3d)
        else:
            raise e
    return data3d

def get_records(force=True):
    if not data3d or force:
        load_records()
    return list(copy.deepcopy(data3d))


def get_record_by_key_val(key:str, val:str, update:bool=False):
    global data3d
    data3d = load_records()

    i = -1
    res = None
    for index, item in enumerate(data3d):
        if item[key] == val:
            i = index
            res = item
            break

    if i > -1 and update:
        del data3d[i]
        data3d.appendleft(res)
        save(list(data3d))
    
    return copy.deepcopy(res)

def get_record_by_prompt(prompt:str, update:bool=False):
    return get_record_by_key_val('prompt', prompt, update)


def get_record_by_image(filepath:str, update:bool=False):
    return get_record_by_key_val('file_image', filepath, update)

def get_record_by_id(_id:str, update:bool=False):
    return get_record_by_key_val('id', _id, update)

def del_record_by_id(_id:str):
    global data3d
    data3d = load_records()

    i = -1
    for index, item in enumerate(data3d):
        if item['id'] == _id:
            i = index
            break

    if i > -1:
        del data3d[i]
        save(list(data3d))