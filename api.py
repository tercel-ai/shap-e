from config import config
import requests

class APIExcepiton(Exception):
    pass

create_by = config.get('SHAPE_CREATE_BY', {})


def api_text_to_3d(prompt):
    if create_by.get('name') == 'DreamMaker':
        return api_text_to_3d_dreammaker(prompt)
    else:
        raise APIExcepiton('unknown create_by')

def api_text_to_3d_dreammaker(prompt):
    res = requests.post(url=create_by.get('url'), headers={'Content-Type': 'application/json'}, json={'text': prompt})
    res = res.json()
    if res.get('code') != 200 or not res.get('data'):
        raise APIExcepiton('fail to create')

    data = {
        'from': 'text',
        'prompt': prompt,
        'file_image': '',
        'file_3d': res['data']
    }
    return data
    