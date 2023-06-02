import json
import os
from collections import deque

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
