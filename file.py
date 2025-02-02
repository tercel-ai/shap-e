import os
import hashlib
from log import logger

dir_path = 'statics'

class FileExcepiton(Exception):
    pass

def upload_file(file):
    ext = os.path.splitext(file.filename)[1]
    if ext.lower() not in ['.bmp','.png','.jpg','.jpeg']:
        raise FileExcepiton('Illegal file')
    
    md5 = hashlib.md5()
    while True:
        data = file.read(8192)
        if not data:
            break
        md5.update(data)
    file_md5 = md5.hexdigest()

    new_filename = file_md5 + ext
    file.seek(0)
    file.save(os.path.join(dir_path, new_filename))
    return f'{dir_path}/{new_filename}', file_md5

def delete_file(filepath):
    if not filepath:
        return False
    try:
        os.remove(filepath)
        return True
    except OSError as e:
        logger.error(f'can not delete {filepath}: {e.strerror}')
        return False