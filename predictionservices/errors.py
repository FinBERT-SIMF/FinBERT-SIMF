
class DataProvidingException(Exception):
    def __init__(self, message, code=500):
        Exception.__init__(self)
        self.message = message
        self.code = code