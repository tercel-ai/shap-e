import argparse
from web.webdata import webdata, save, md5
from log import logger

parser = argparse.ArgumentParser(description='Generate 3D')
parser.add_argument('action', type=str, help='<reset|update>')
parser.add_argument('--data', type=str, help='input json string', default='{}')


args = parser.parse_args()
logger.debug('args:%s', args)

def reset():
    global webdata
    for index, item in enumerate(webdata):
        if 'id' not in item:
            if not item.get('prompt'):
                arr = item['file_image'].split('/')
                item['id'] = arr[len(arr)-1].split('.')[0]
                item['from'] = 'image'
            else:
                item['id'] = md5(item['prompt'])
                item['from'] = 'text'
    
    save(list(webdata))

if __name__ == '__main__':
    if args.action == 'reset':
        reset()
