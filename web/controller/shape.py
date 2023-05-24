from web.app import http_app, request
from web.apimsg import ApiMessage
import json
import time
import asyncio
from entry import can_create, text_to_3d, clear_files, get_files, dir_path
from web.webdata import save_record, get_records, get_record_by_prompt

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

    prompt = prompt.strip().lower()
    if not prompt:
        return ApiMessage.fail('please input a prompt').to_dict()
    
    d = get_record_by_prompt(prompt)
    if d:
        d['file_image'] = get_file_url(d['file_image'])
        d['file_3d'] = get_file_url(d['file_3d'])
        return ApiMessage.success(d).to_dict()
    
    name = str(now_full_int())
    # asyncio.run(create_3d(prompt, name))
    text_to_3d(prompt, name)
    data = {
        'prompt': prompt,
        'file_image': f"{dir_path}/{name}.gif",
        'file_3d': f"{dir_path}/{name}.0.ply"
    }
    save_record(data)
    res = {
        'prompt': prompt,
        'file_image': f"{request.host_url}{dir_path}/{name}.gif",
        'file_3d': f"{request.host_url}{dir_path}/{name}.0.ply"
    }
    return ApiMessage.success(res).to_dict()


@http_app.route("/v1/shape/records", methods=['GET'])
def shape_records():
    data = get_records()
    for d in data:
        d['file_image'] = get_file_url(d['file_image'])
        d['file_3d'] = get_file_url(d['file_3d'])

    return ApiMessage.success(data).to_dict()


def get_file_url(filename:str):
    return f"{request.host_url}{filename}"

