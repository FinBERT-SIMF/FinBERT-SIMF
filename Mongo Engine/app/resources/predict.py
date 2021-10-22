from flask import request, json, Response
from flask_restful import Resource
# from flask_apispec import marshal_with
from app.response import ResponseAPI
from app.errors import CustomException
from app.model.predictModel import PredictModel
import logging as log
from datetime import datetime


class Predict(Resource):
    @classmethod
    def post(cls):
        try:
            data = request.json
            log.info(data)
            predictModel = PredictModel()
            data = predictModel.validatData(data)
            if data:
                response = predictModel.save_to_DB(data)
                if response:
                    return ResponseAPI.send(status_code=200, message="Inserted successfully", data=str(response))
                else:
                    return ResponseAPI.send(status_code=404, message="Database Connection Error")
            else:
                # 404 status code for duplicated news item
                return ResponseAPI.send(status_code=404, message="Database Connection Error")
        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent parameters format or duplicated Timestamp!")

        except Exception:
            raise CustomException("user_error", 500, 2201)

    @classmethod
    def get(cls):
        try:
            args = request.args
            log.info(args)
            if args is None or args == {}:
                return ResponseAPI.send(status_code=400, message="Please provide request parameters information")

            elif args.get('timestamp') and args.get('pair') and args.get('resolution') and args.get('category'):
                obj1 = PredictModel()
                response = obj1.getPredictedPrice(timestamp=args['timestamp'], pair=args['pair']
                                                  , resolution=args['resolution'], category=args['category'])
                return ResponseAPI.send(status_code=200, message="Successful", data=response)

            elif args.get('category') and args.get('pair') and args.get('resolution') and args.get('from') and args.get(
                    'to'):
                obj2 = PredictModel()
                response = obj2.find_by_date_symbol_resolution(symbol=args['pair'], start=args['from']
                                                               , end=args['to'], resolution=args['resolution']
                                                               )


                return ResponseAPI.send(status_code=200, message="Successful", data=response)

            elif args.get('category') and args.get('pair') and args.get('resolution') and args.get('from') is None:
                obj1 = PredictModel()
                ts = int(datetime.utcnow().timestamp())
                ts = ts - (ts % 1800)  # round to nearest hour
                ts = ts + 3600
                print(ts)

                response = obj1.find_by_date_pair_category(pair=args['pair'], category=args['category'], timestamp=ts)

                return ResponseAPI.send(status_code=200, message="Successful", data=response)



        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent date format!", data=False)
