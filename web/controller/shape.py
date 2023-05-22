from app import http_app, request
from apimsg import ApiMessage
import json
import time
import asyncio
from create import create_3d, can_create

def now_full_int():
    return int(time.time()*1000000)


@http_app.route("/v1/shape/create", methods=['POST'])
def shape_create():
    data = json.loads(request.data)
    if not can_create():
        return ApiMessage.fail('busy, please wait a moment').to_dict()
    
    if not data.get('prompt'):
        return ApiMessage.fail('please input a prompt').to_dict()

    name = str(now_full_int())
    filename = name+'.1.ply'
    asyncio.run(create_3d(data['prompt']))
    return ApiMessage.success(filename).to_dict()


@http_app.route("/v1/shape/get-file", methods=['GET'])
def shape_get_file():
    filename = request.args.get('filename', '')
    #todo 
    filepath = request.url + 'files/'+filename
    return ApiMessage.success(filepath).to_dict()