from web.app import http_app, request
from web.apimsg import ApiMessage
import json
import time
import asyncio
from entry import can_create, text_to_3d, clear_files, get_files, dir_path
from web.webdata import save_record, get_records

def now_full_int():
    return int(time.time()*1000000)


@http_app.route("/v1/shape/create", methods=['POST'])
def shape_create():
    param = json.loads(request.data)
    if not can_create():
        return ApiMessage.fail('busy, please wait a moment').to_dict()
    
    prompt = param.get('prompt')
    if not prompt:
        return ApiMessage.fail('please input a prompt').to_dict()

    name = str(now_full_int())
    # asyncio.run(create_3d(prompt, name))
    text_to_3d(prompt, name)
    data = {
        'prompt': prompt,
        'file_image': f"{name}.gif",
        'file_3d': f"{name}.0.ply"
    }
    save_record(data)
    res = {
        'prompt': prompt,
        'file_image': f"{request.host_url}{dir_path}/{name}.gif",
        'file_3d': f"{request.host_url}{dir_path}/{name}.0.ply"
    }
    return ApiMessage.success(res).to_dict()


@http_app.route("/v1/shape/get_records", methods=['GET'])
def get_records():
    data = get_records()
    for d in data:
        file_image = d['file_image']
        d['file_image'] = f"{request.host_url}{dir_path}/{file_image}",
        file_3d = d['file_3d']
        d['file_3d'] = f"{request.host_url}{dir_path}/{file_3d}",

    return ApiMessage.success(data).to_dict()


