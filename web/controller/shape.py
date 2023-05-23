from web.app import http_app, request
from web.apimsg import ApiMessage
import json
import time
import asyncio
from entry import create_3d, can_create, generate_ply, clear_files, get_files

def now_full_int():
    return int(time.time()*1000000)


@http_app.route("/v1/shape/create", methods=['POST'])
def shape_create():
    data = json.loads(request.data)
    if not can_create():
        return ApiMessage.fail('busy, please wait a moment').to_dict()
    
    prompt = data.get('prompt')
    if not prompt:
        return ApiMessage.fail('please input a prompt').to_dict()

    name = str(now_full_int())
    filename = name+'.0.ply'
    # asyncio.run(create_3d(data['prompt']))
    generate_ply(prompt, name)
    filepath = request.host_url + 'statics/'+filename
    return ApiMessage.success(filepath).to_dict()


@http_app.route("/v1/shape/get-file", methods=['GET'])
def shape_get_file():
    filename = request.args.get('filename', '')
    #todo 
    filepath = request.host_url + 'statics/'+filename
    return ApiMessage.success(filepath).to_dict()


@http_app.route("/v1/shape/clear-files", methods=['POST'])
def shape_clear_files():
    clear_files()
    return ApiMessage.success().to_dict()


@http_app.route("/v1/shape/show-files", methods=['GET'])
def shape_show_files():
    data = get_files()
    return ApiMessage.success(data).to_dict()

