from web.app import http_app, request
from web.apimsg import ApiMessage
import json
import time
import hashlib
import os
import copy
# from entry import can_create, text_to_3d, image_to_3d, now_full_int, delete_file, ParamExcepiton
from data3d import add_record, get_records, get_record_by_id, md5
from datatask import add_task_data, get_task_data_by_id, len_task_data
from file import upload_file
from log import logger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def get_remote_ip():
    remote_addr = get_remote_address()
    x_real_ip = request.headers.get('X-Real-IP')
    if x_real_ip:
        remote_addr = x_real_ip
    
    return remote_addr

limit_time = os.environ.get('SHAPE_CREATE_LIMIT_TIME', "5 per day")
limiter = Limiter(
    app=http_app,
    key_func=get_remote_ip,
    default_limits=[limit_time],
    exempt_routes=["/v1/shape/records", "/v1/shape/record"]
)

def str_to_bool(str):
    if str.lower() in ['true', 'yes', '1']:
        return True
    return False


# @http_app.route("/v1/shape/create_by_text", methods=['GET','POST'])
# @limiter.limit(limit_time)
# def shape_create_by_text():
#     param = dict()
#     try:
#         param = json.loads(request.data)
#     except:
#         pass

#     prompt = param.get('prompt')
#     if not prompt:
#         prompt = request.args.get('prompt')
#         param['prompt'] = prompt
#     if not prompt:
#         return ApiMessage.fail('please input a prompt').to_dict()

#     prompt = prompt.strip().lower()
#     if not prompt:
#         return ApiMessage.fail('please input a prompt').to_dict()
    
#     if not can_create():
#         return ApiMessage.fail('busy, please wait a moment').to_dict()
    
#     _id = md5(prompt)
#     d = get_record_by_id(_id, True)
#     if d:
#         d.update(show_data(d))
#         return ApiMessage.success(d).to_dict()
    
#     name = str(now_full_int())
#     file_image, file_3d = text_to_3d(prompt, name)
#     data = {
#         'id': _id,
#         'from': 'text',
#         'prompt': prompt,
#         'file_image': file_image,
#         'file_3d': file_3d[0]
#     }
#     add_record(data)
#     res = show_data(data)
#     return ApiMessage.success(res).to_dict()


# @http_app.route("/v1/shape/create_sync", methods=['POST'])
# @limiter.limit(limit_time)
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
@limiter.limit(limit_time)
def shape_create():
    prompt = request.form.get('prompt')
    file = request.files.get('image')

    logger.debug('shape_create prompt:%s', prompt)
    logger.debug('shape_create file:%s', file)

    if not prompt and not file:
        return ApiMessage.fail('please input a prompt or upload a picture').to_dict()

    if file and not file.filename:
        return ApiMessage.fail('please upload a picture').to_dict()

    if not prompt:
        prompt = ''
    prompt = prompt.strip().lower()
    
    if len_task_data() > 0:
        return ApiMessage.fail('busy, please wait a moment').to_dict()
    

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
        return ApiMessage.fail().to_dict()


@http_app.route("/v1/shape/records", methods=['GET'])
def shape_records():
    force = str_to_bool(request.args.get('force', ''))
    data = get_records(force)
    for d in data:
        d.update(show_data(d))

    return ApiMessage.success(data).to_dict()


@http_app.route("/v1/shape/record", methods=['GET'])
def shape_record():
    _id = request.args.get('id', '')
    d = get_record_by_id(_id)
    if d:
        d.update(show_data(d))
        return ApiMessage.success(d).to_dict()
    
    d = get_task_data_by_id(_id)
    if d:
        return ApiMessage.success(d).to_dict()
    else:
        return ApiMessage.fail().to_dict()


def get_file_url(filename:str):
    return f"{request.host_url}{filename}"

def show_data(data: dict):
    res = copy.deepcopy(data)
    res['file_image'] = get_file_url(data.get('file_image', ''))
    res['file_3d'] = get_file_url(data.get('file_3d', ''))
    return res
