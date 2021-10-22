from flask import request, json, Response
from flask_restful import Resource
#from flask_apispec import marshal_with
from app.response import ResponseAPI
from app.errors import CustomException
from app.model.newsModel import NewsModel
import logging as log
import json

# todo: resp.statuscode need to be set. I only set status code in resp Object
class News(Resource):
    @classmethod
    # @marshal_with(NewsModelSchema)
    def post(cls):
        try:
            data = request.json
            log.info(data)
            newsModel = NewsModel()
            #print(data)
            data = newsModel.validatData(data)
            if data:

                if not newsModel.find_by_Link(data['link']):
                    response = newsModel.save_to_DB(data)
                    if response:

                        return ResponseAPI.send(status_code=200, message="Inserted successfully", data=str(response))
                    else:
                        return ResponseAPI.send(status_code=404, message="Database Connection Error")
                else:
                    # 404 status code for duplicated news item
                    return ResponseAPI.send(status_code=404, message="Duplicated News Item")
        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent parameters format!")

        except Exception:
            raise CustomException("user_error", 500, 2201)
    @classmethod
    def get(cls):
        try:
            args = request.args
            log.info(args)
            args.get('link')

            if args is None or args == {}:
                return ResponseAPI.send(status_code=400, message="Please provide request parameters information")

            elif args.get('link') is not None:
                obj1 = NewsModel()
                response = obj1.find_by_Link(args['link'])
                if response:
                    message = "Exist"
                else:
                    message = "Not Exist"

                return ResponseAPI.send(status_code=200, message=message, data=response)
            elif args.get('category') == "all":
                obj1 = NewsModel()
                print(args)
                response = obj1.read()
                print(response)
                return ResponseAPI.send(status_code=200, message="Successfully", data=json.dumps(response, indent=3))

            elif args.get('keywords') and args.get('from') and args.get('to') and args.get('category'):
                log.info("search in mongo")
                start = int(args['from'])
                end = int(args['to'])

                if start < end:
                    obj1 = NewsModel()

                    response = obj1.find_by_date_keyword_category(args['keywords'], start, end, args['category'])
                    print(response)
                    if response is None and response == {}:
                        return ResponseAPI.send(status_code=200, message="No item")
                    else:
                        return ResponseAPI.send(status_code=200, message="Successfully", data=json.dumps(response))

                else:
                    raise ValueError(
                        "Error: The second date input is earlier than the first one")
            elif args.get('category').lower() in ["cryptocurrency", "forex", "commodities"] and \
                    args.get('keywords') and args.get('from') is None:
                obj1 = NewsModel()
                response = obj1.find_by_keywords(args.get('category'), args.get('keywords'))
                return ResponseAPI.send(status_code=200, message="Successfully", data=json.dumps(response, indent=3))
            elif args.get('category').lower() in ["cryptocurrency", "forex", "commodities"] and args.get(
                    'keywords') is None:
                obj1 = NewsModel()
                response = obj1.find_by_category(args.get('category'))
                return ResponseAPI.send(status_code=200, message="Successfully", data=json.dumps(response, indent=3))

            else:

                return ResponseAPI.send(status_code=422, message="Bad Request Parameters!", data=False)
        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent date format!", data=False)
