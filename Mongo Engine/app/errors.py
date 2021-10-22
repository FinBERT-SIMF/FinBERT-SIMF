from flask import jsonify


class CustomException(Exception):
    def __init__(self, message, status=400, code=None):
        Exception.__init__(self)
        self.message = message
        self.status = status
        self.code = code


class BadRequest(CustomException):
    """Custom exception class to be thrown when local error occurs."""
    message = "hi"
    status = 400
    code = 12345


class NoResultFound(CustomException):
    code = 102
    message = "Result Not Found"


def init_error_handeler(app):
    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        """Catch BadRequest exception globally, serialize into JSON, and respond with 400."""
        message = error.message
        status_code = error.status
        response = {
            'status': status_code,
            'error': {
                'type': error.__class__.__name__,
                'message': message,
                'code': error.code
            }
        }
        return jsonify(response), status_code

    #@app.errorhandler(Exception)
    def handle_error(error):
        print(error)
        message = [str(x) for x in error.args]
        status_code = 500
        response = {
            'status': 500,
            'error': {
                'type': error.__class__.__name__,
                'message': message,
                'code': '100'
            }
        }

        return jsonify(response), status_code
