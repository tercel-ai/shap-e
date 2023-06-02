import json
import os
from collections import deque
import copy

max_records = int(os.environ.get('SHAPE_DATATASK_MAX', 2))

datatask = deque([]);


class DataTaskExcepiton(Exception):
    pass

def save(_data: list):
    try:
        json_str = json.dumps(_data)
        with open('.datatask.json', 'w') as f:
            f.write(json_str)
    except Exception as e:
        raise DataTaskExcepiton(str(e))

    
def add_task_data(data:dict):
    global datatask
    if len(datatask) > max_records:
        return False
        
    datatask.appendleft(data)
    save(list(datatask))
    return True

def load_task_data(force=False):
    global datatask
    try:
        with open('.datatask.json', 'r') as f:
            json_str = f.read()
        datatask = deque(json.loads(json_str))
    except Exception as e:
        if force:
            datatask = []
            save(datatask)
        else:
            raise e
    return datatask

def clear_task_data():
    save([])

def len_task_data():
    data = load_task_data()
    return len(data)

def get_task_data_by_key_val(key:str, val:str):
    global datatask
    datatask = load_task_data()
    for index, item in enumerate(datatask):
        if item[key] == val:
            return copy.deepcopy(item)

    return None


def get_task_data_by_id(_id:str):
    return get_task_data_by_key_val('id', _id)
