from web.app import http_app, request
from web.apimsg import ApiMessage
import json
import time
import hashlib
import os
import copy
# from entry import can_create, text_to_3d, image_to_3d, now_full_int, delete_file, ParamExcepiton
from data3d import add_record, get_records, get_record_by_id, md5, del_record_by_id, clear_invalid_records
from datatask import add_task_data, get_task_data_by_id, len_task_data
from datatop import get_records as tops
from file import upload_file
from log import logger
from config import config
from flask_limiter.util import get_remote_address
from api import api_text_to_3d

def get_remote_ip():
    remote_addr = get_remote_address()
    x_real_ip = request.headers.get('X-Real-IP')
    if x_real_ip:
        remote_addr = x_real_ip
    logger.debug('client ip address:%s', remote_addr)
    return remote_addr

limit_time = config.get('SHAPE_CREATE_LIMIT_TIME', 86400)
white_list = config.get('SHAPE_CREATE_WHITE_LIST', '')
create_by = config.get('SHAPE_CREATE_BY')

created_records = dict()


def check_expired(ip):
    global created_records
    created_time = created_records.get(ip)
    if created_time and created_time + limit_time > time.time():
        return False
    
    created_records[ip] = time.time()
    return True

def clear_expired():
    global created_records
    ips = list(created_records.keys())
    for ip in ips:
        if check_expired(ip):
            del created_records[ip]


def check_limit():
    try:
        clear_expired()
    except:
        pass
    
    ip = get_remote_ip()
    if ip in white_list.split(','):
        return True
    
    return check_expired(ip)


def str_to_bool(str):
    if str.lower() in ['true', 'yes', '1']:
        return True
    return False


@http_app.route("/v1/shape/create_by_text", methods=['GET','POST'])
def shape_create_by_text():
    if not create_by:
        return ApiMessage.fail('disabled').to_dict()
    
    param = dict()
    try:
        param = json.loads(request.data)
    except:
        pass

    prompt = param.get('prompt')
    if not prompt:
        prompt = request.form.get('prompt')
    if not prompt:
        prompt = request.args.get('prompt')
        
    if not prompt:
        return ApiMessage.fail('please input a prompt').to_dict()

    prompt = prompt.strip().lower()
    if not prompt:
        return ApiMessage.fail('please input a prompt').to_dict()
    
    _id = md5(prompt)
    d = get_record_by_id(_id, True)
    if d:
        d.update(show_data(d))
        return ApiMessage.success(d).to_dict()
    
    data = api_text_to_3d(prompt)
    data['id'] = _id
    add_record(data)
    res = show_data(data)
    return ApiMessage.success(res).to_dict()


# @http_app.route("/v1/shape/create_sync", methods=['POST'])
# def shape_create_sync():
#     prompt = request.form.get('prompt')
#     file = request.files.get('image')

#     logger.debug('shape_create prompt:%s', prompt)
#     logger.debug('shape_create file:%s', file)

#     if not prompt and not file:
#         return ApiMessage.fail('please input a prompt or upload a picture').to_dict()

#     if file and not file.filename:
#         return ApiMessage.fail('please upload a picture').to_dict()

#     if not prompt:
#         prompt = ''
#     prompt = prompt.strip().lower()
    
#     if not can_create():
#         return ApiMessage.fail('busy, please wait a moment').to_dict()
    
#     name = str(now_full_int())
    
#     data = dict()
#     if file:
#         from_image, file_name = upload_file(file)
#         time.sleep(0.1)
#         _id = file_name
#         d = get_record_by_id(_id, True)
#         if d:
#             d.update(show_data(d))
#             return ApiMessage.success(d).to_dict()
        
#         file_image, file_3d = image_to_3d(from_image, name)
#         delete_file(from_image)
#         data = {
#             'id':_id,
#             'from': 'image',
#             'prompt': prompt,
#             'file_image': file_image,
#             'file_3d': file_3d[0]
#         }
#     elif prompt:
#         _id = md5(prompt)
#         d = get_record_by_id(_id, True)
#         if d:
#             d.update(show_data(d))
#             return ApiMessage.success(d).to_dict()
        
#         file_image, file_3d = text_to_3d(prompt, name)
#         data = {
#             'id': _id,
#             'from': 'text',
#             'prompt': prompt,
#             'file_image': file_image,
#             'file_3d': file_3d[0]
#         }

#     if data:
#         add_record(data)
#         res = show_data(data)
#         return ApiMessage.success(res).to_dict()
#     else:
#         return ApiMessage.fail().to_dict()
    

@http_app.route("/v1/shape/create", methods=['POST'])
def shape_create():
    prompt = request.form.get('prompt')
    file = request.files.get('image')

    # logger.debug('shape_create prompt:%s', prompt)
    # logger.debug('shape_create file:%s', file)

    if not prompt and not file:
        return ApiMessage.fail('please input a prompt or upload a picture').to_dict()

    if file and not file.filename:
        return ApiMessage.fail('please upload a picture').to_dict()

    if not prompt:
        prompt = ''
    prompt = prompt.strip().lower()
    
    if len_task_data() > 0:
        return ApiMessage.fail('Service is busy, please try again later').to_dict()
    
    if not check_limit():
        return ApiMessage.fail('Request Limit Exceeded. You have reached your maximum allowed requests today.').to_dict()

    clear_invalid_records()
    
    data = dict()
    if file:
        from_image, file_name = upload_file(file)
        time.sleep(0.1)
        _id = file_name
        d = get_record_by_id(_id, True)
        if d:
            d.update(show_data(d))
            return ApiMessage.success(d).to_dict()
        
        data = {
            'id':_id,
            'from': 'image',
            'prompt': prompt,
            'file_image': from_image,
            'file_3d': ''
        }
        add_task_data(data)
        return ApiMessage.success(data).to_dict()
        
    elif prompt:
        _id = md5(prompt)
        d = get_record_by_id(_id, True)
        if d:
            d.update(show_data(d))
            return ApiMessage.success(d).to_dict()
        
        data = {
            'id': _id,
            'from': 'text',
            'prompt': prompt,
            'file_image': '',
            'file_3d': ''
        }
        add_task_data(data)
        return ApiMessage.success(data).to_dict()

    else:
        return ApiMessage.fail('invalid parameter').to_dict()


@http_app.route("/v1/shape/records", methods=['GET'])
def shape_records():
    force = str_to_bool(request.args.get('force', ''))
    data = get_records(force)
    for i in range(len(data)):
        if 'errmsg' in data[i]:
            del data[i]

    for d in data:
        d.update(show_data(d))

    return ApiMessage.success(data).to_dict()


@http_app.route("/v1/shape/record", methods=['GET'])
def shape_record():
    _id = request.args.get('id', '')
    d = get_record_by_id(_id)
    if d:
        if 'errmsg' in d:
            del_record_by_id(d['id'])
            return ApiMessage.fail(d['errmsg']).to_dict()
        
        d.update(show_data(d))
        return ApiMessage.success(d).to_dict()
    
    d = get_task_data_by_id(_id)
    if d:
        return ApiMessage.success(d).to_dict()
    else:
        return ApiMessage.fail('invalid id').to_dict()
    

@http_app.route("/v1/shape/tops", methods=['GET'])
def shape_tops():
    force = str_to_bool(request.args.get('force', ''))
    data = tops(force)
    for i in range(len(data)):
        if 'errmsg' in data[i]:
            del data[i]

    for d in data:
        d.update(show_data(d))

    return ApiMessage.success(data).to_dict()


def get_file_url(filename:str):
    if not filename:
        return ""
    if filename.find('http://') == 0 or filename.find('https://') == 0:
        return filename
    
    return f"{request.host_url}{filename}"

def show_data(data: dict):
    res = copy.deepcopy(data)
    res['file_image'] = get_file_url(data.get('file_image', ''))
    res['file_3d'] = get_file_url(data.get('file_3d', ''))
    return res
