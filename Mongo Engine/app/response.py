from flask import Response, jsonify


class ResponseAPI:

    @staticmethod
    def send(status_code, message='', data=None):
        resp = Response({
            "status": status_code,
            "message": message,
            "data": data
        },
            status=status_code
        )
        print(resp.response)

        return resp.response
