import json
import copy
import os
import hashlib
from datetime import datetime, timezone
from collections import deque

max_records = int(os.environ.get('SHAPE_DATA_TOP_MAX', 4))

datatop = deque([]);


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
        with open('.datatop.json', 'w') as f:
            f.write(json_str)
    except Exception as e:
        raise Data3DExcepiton(str(e))
    
def add_record(data:dict):
    data['created_at'] = now_utc_str()
    global datatop
    datatop = load_records()
    try:
        if len(datatop) > max_records:
            d = datatop.pop()
            delete_file(d['file_image'])
            delete_file(d['file_3d'])

        datatop.appendleft(data)
        save(list(datatop))
    except Exception as e:
        raise Data3DExcepiton(str(e))


def load_records(force=False):
    global datatop
    try:
        with open('.datatop.json', 'r') as f:
            json_str = f.read()
        datatop = deque(json.loads(json_str))
    except Exception as e:
        if force:
            datatop = []
            save(datatop)
        else:
            raise e
    return datatop

def get_records(force=True):
    if not datatop or force:
        load_records()
    return list(copy.deepcopy(datatop))


def get_record_by_key_val(key:str, val:str, update:bool=False):
    global datatop
    datatop = load_records()

    i = -1
    res = None
    for index, item in enumerate(datatop):
        if item[key] == val:
            i = index
            res = item
            break

    if i > -1 and update:
        del datatop[i]
        datatop.appendleft(res)
        save(list(datatop))
    
    return copy.deepcopy(res)

def get_record_by_prompt(prompt:str, update:bool=False):
    return get_record_by_key_val('prompt', prompt, update)


def get_record_by_image(filepath:str, update:bool=False):
    return get_record_by_key_val('file_image', filepath, update)

def get_record_by_id(_id:str, update:bool=False):
    return get_record_by_key_val('id', _id, update)

def del_record_by_id(_id:str):
    global datatop
    datatop = load_records()

    i = -1
    for index, item in enumerate(datatop):
        if item['id'] == _id:
            i = index
            break

    if i > -1:
        delete_file(datatop[i]['file_image'])
        delete_file(datatop[i]['file_3d'])
        del datatop[i]
        save(list(datatop))

def clear_invalid_records():
    global datatop
    datatop = load_records()
    found = False
    for i in range(len(datatop)):
        if 'errmsg' in datatop[i]:
            found = True
            delete_file(datatop[i]['file_image'])
            delete_file(datatop[i]['file_3d'])
            del datatop[i]

    if found:
        save(list(datatop))