from web.app import http_app
import os
from web.controller import *

if __name__ == '__main__':
    http_app.run(host=os.environ.get('SHAPE_WEB_HOST', '0.0.0.0'), port=os.environ.get('SHAPE_WEB_PORT', '5001'))