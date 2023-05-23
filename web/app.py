from flask import Flask, request
from flask_cors import CORS
from web.apimsg import ApiMessage

http_app = Flask(__name__, static_folder='statics')
CORS(http_app, resources={r'/*': {'origins': '*'}})


def check_token(request):
    # todo
    return True

@http_app.route("/", methods=['GET', 'POST'])
def home():
    return ApiMessage.success('Welcome').to_dict()


@http_app.before_request
def before_request():
    no_check = ['/', '/v1/user/login']
    if request.path not in no_check :
        res = check_token(request)
        if (res == False):
            return ApiMessage.error(401, 'Unauthorized').to_dict(), 401
        

@http_app.errorhandler(Exception)
def handle_error(e):
    return ApiMessage.error(500, str(e)).to_dict(), 500