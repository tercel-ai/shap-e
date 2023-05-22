class ApiMessage(object):
    """rest api response message"""
    def __init__(self, code=0, msg='', data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def to_dict(self):
        # todo handle special type data
        return self.__dict__
          
    @staticmethod
    def error(code, msg='', data=None):
        return ApiMessage(code, msg, data)
    
    @staticmethod
    def success(data=True):
        return ApiMessage(0, 'success', data)
    
    @staticmethod
    def fail(data=False):
        return ApiMessage(1, 'fail', data)
         
