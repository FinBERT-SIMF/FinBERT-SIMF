from flask import request, json, Response
from flask_restful import Resource
from app.response import ResponseAPI
from app.errors import CustomException
from app.model.conceptsModel import ConceptsModel
import logging as log


class Concepts(Resource):
    @classmethod
    def post(cls):
        try:
            data =json.loads( request.data)
            #print(data)
            conceptsModel = ConceptsModel()
            if data:
                response = conceptsModel.save_to_DB(data)
                if response:
                    return ResponseAPI.send(status_code=200, message="Inserted successfully", data=str(response))
                else:
                    return ResponseAPI.send(status_code=404, message="Database Connection Error")
            else:

                return ResponseAPI.send(status_code=404, message="Database Connection Error")
        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent parameters format!")

        except Exception:
            raise CustomException("user_error", 500, 2201)

    @classmethod
    def get(cls):
        try:
            args = request.args
            log.info(args)
            if args is None or args == {}:
                return ResponseAPI.send(status_code=400, message="Please provide request parameters information")

            elif args.get('pair'):

                obj1 = ConceptsModel()
                response = obj1.find_by_pair(args['pair'])
                return ResponseAPI.send(status_code=200, message="Successful", data=response)

        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent parameter format!", data=False)
