from web.app import http_app, request
from web.apimsg import ApiMessage
import json
import time
from entry import can_create, text_to_3d, image_to_3d, dir_path, upload_file, now_full_int
from web.webdata import save_record, get_records, get_record_by_prompt, get_record_by_image
from log import logger

def str_to_bool(str):
    if str.lower() in ['true', 'yes', '1']:
        return True
    return False


@http_app.route("/v1/shape/create_by_text", methods=['GET','POST'])
def shape_create_by_text():
    param = dict()
    try:
        param = json.loads(request.data)
    except:
        pass

    prompt = param.get('prompt')
    if not prompt:
        prompt = request.args.get('prompt')
        param['prompt'] = prompt
    if not prompt:
        return ApiMessage.fail('please input a prompt').to_dict()

    prompt = prompt.strip().lower()
    if not prompt:
        return ApiMessage.fail('please input a prompt').to_dict()
    
    if not can_create():
        return ApiMessage.fail('busy, please wait a moment').to_dict()
    
    d = get_record_by_prompt(prompt)
    if d:
        d.update(show_data(d))
        logger.debug('from data: %s', prompt)
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
    res = show_data(data)
    return ApiMessage.success(res).to_dict()


@http_app.route("/v1/shape/create", methods=['GET','POST'])
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
    
    if not can_create():
        return ApiMessage.fail('busy, please wait a moment').to_dict()
    

    name = str(now_full_int())
    
    data = dict()
    if file:
        filename = upload_file(file)
        d = get_record_by_image(f"{dir_path}/{filename}")
        if d:
            d.update(show_data(d))
            logger.debug('from data: %s', filename)
            return ApiMessage.success(d).to_dict()
        
        image_to_3d(filename, name)
        data = {
            'prompt': prompt,
            'file_image': f"{dir_path}/{filename}",
            'file_3d': f"{dir_path}/{name}.0.ply"
        }
    elif prompt:
        d = get_record_by_prompt(prompt)
        if d:
            d.update(show_data(d))
            logger.debug('from data: %s', prompt)
            return ApiMessage.success(d).to_dict()
        
        text_to_3d(prompt, name)
        data = {
            'prompt': prompt,
            'file_image': f"{dir_path}/{name}.gif",
            'file_3d': f"{dir_path}/{name}.0.ply"
        }

    if data:
        save_record(data)
        res = show_data(data)
        return ApiMessage.success(res).to_dict()
    else:
        return ApiMessage.fail().to_dict()


@http_app.route("/v1/shape/records", methods=['GET'])
def shape_records():
    force = str_to_bool(request.args.get('force', ''))
    data = get_records(force)
    for d in data:
        d.update(show_data(d))

    return ApiMessage.success(data).to_dict()


def get_file_url(filename:str):
    return f"{request.host_url}{filename}"

def show_data(data: dict):
    res = {
        'prompt': data.get('prompt', ''),
        'file_image': get_file_url(data.get('file_image', '')),
        'file_3d': get_file_url(data.get('file_3d', ''))
    }
    return res
