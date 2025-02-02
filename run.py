from entry import text_to_3d, image_to_3d, now_full_int, delete_file, ParamExcepiton
from log import logger
from datatask import load_task_data, clear_task_data
from data3d import add_record
import time

def create_3d(data: dict):
    name = str(now_full_int())
    if data['from'] == 'text':
        file_image, file_3d = text_to_3d(data['prompt'], name)
        data['file_image'] = file_image
        data['file_3d'] = file_3d[0]
        try:
            add_record(data)
        except Exception as e:
            errmsg = 'text_to_3d except: ' + str(e)
            data['errmsg'] = errmsg
            add_record(data)
            logger.error(errmsg)

    elif data['from'] == 'image':
        try:
            file_image, file_3d = image_to_3d(data['file_image'], name)
            delete_file(data['file_image'])
            data['file_image'] = file_image
            data['file_3d'] = file_3d[0]
            add_record(data)
        except Exception as e:
            delete_file(data['file_image'])
            errmsg = 'image_to_3d except: ' + str(e)
            data['errmsg'] = errmsg
            add_record(data)
            logger.error(errmsg)
    else:
        logger.error('unknown from data:%s', data)

def main():
    logger.info('run create 3d ...')
    while True:
        data = load_task_data(True)
        while len(data) > 0:
            d = data.pop()
            if not d:
                continue;
            
            start = time.time()
            try:
                create_3d(d)
                logger.debug('create 3d:%s, time:%s', d, time.time()-start)
            except:
                pass
            time.sleep(0.05)

        clear_task_data()
        time.sleep(0.1)

if __name__ == '__main__':
    main()