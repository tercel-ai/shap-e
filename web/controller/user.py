from app import http_app, request
from apimsg import ApiMessage
import json

@http_app.route("/v1/user/login", methods=['POST'])
def login():
    data = json.loads(request.data)
    return ApiMessage.success(data).to_dict()