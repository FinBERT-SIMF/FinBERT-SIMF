from flask import request, json, Response
from flask_restful import Resource
from app.response import ResponseAPI
from app.errors import CustomException
from app.model.candleModel import CandleModel
import logging as log


class Candle(Resource):
    @classmethod
    def post(cls):
        try:
            data = request.json

            log.info(data['resolution'])
            candleModel = CandleModel()

            if data:
                response = candleModel.save_many_DB(data)
                if response:
                    return ResponseAPI.send(status_code=200, message="Inserted successfully", data=str(response))
                else:
                    return ResponseAPI.send(status_code=404, message="Database Connection Error")
            else:
                # 404 status code for duplicated news item
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

            elif args.get('symbol') and args.get('from') and args.get('to') and args.get('resolution'):

                obj1 = CandleModel()
                res = obj1.validatData(args.get('symbol'), args.get('resolution'), args.get('from'), args.get('to'))

                response = obj1.find_by_date_symbol_resolution(symbol=args['symbol'], start=args['from'],
                                                               end=args['to'], resolution=str(args['resolution']))

                return ResponseAPI.send(status_code=200, message="Successful", data=response)
            elif args.get('symbol'):
                obj1 = CandleModel()
                response = obj1.find_by_symbol(args.get('symbol'))
                print(response)
                return ResponseAPI.send(status_code=200, message="Successful", data=response)

        except ValueError:

            return ResponseAPI.send(status_code=422, message="Inconsistent parameter format!", data=False)
