from flask_restful import Resource
from flask import request
from app.response import ResponseAPI
import requests
import pandas as pd
from datetime import datetime
import json

def prepaireCandels(category, pair, startDate, endDate, resolution=60):
    '''
        :param category: currency pair category
        :param pair: symbol
        :param startDate: from timestamp
        :param endDate: to timestamp
        :param resolution: timeframe
        :return: DataFrame
        :exception: DataProvidingException when fail to connect to finnhub
        '''
    # I manualy determine the startDate because I itself calculate indicator values
    # delayForINdicators = SEQ_LEN * 60 * 60 * 60
    startDate = int(startDate)
    endDate = int(endDate)
    # endDate = int(endDate)
    try:
        
        if category.lower() == "forex":
            symbol = 'OANDA:'
            symbol = symbol + pair[0:3].upper() + '_' + pair[3:].upper()
        elif category.lower() == "cryptocurrency":
            symbol = 'BINANCE:'
            if pair.upper().find('BTCUSD') != -1:
                symbol = symbol + 'BTCUSDT'
            category = 'crypto'

        queryString = 'https://finnhub.io/api/v1/' + category.lower() + '/candle?symbol=' + symbol \
                      + '&resolution=' + str(resolution) + '&from='
        queryString += str(startDate) + '&to=' + str(endDate) + '&token=bveu6qn48v6rhdtufjbg'

        print(queryString)

       
        r = requests.get(queryString)

        if r.status_code == 200 and r.json() is not None:
            print("I am here3")
            df = pd.DataFrame(r.json())
            print("I am here2")

            df['close'] = df['c']
            df = df.drop('c', 1)

            df['open'] = df['o']
            df = df.drop('o', 1)

            df['low'] = df['l']
            df = df.drop('l', 1)

            df['high'] = df['h']
            df = df.drop('h', 1)

            df = df.drop('s', 1)

            df['timestamp'] = df['t']
            df = df.drop('t', 1)

            df['volume'] = df['v']
            df = df.drop('v', 1)

           
            return df
        else :
            raise ValueError
    except ConnectionError as err:
        return False
    except OSError as err:
        return False
    except Exception as err:
        return False


class Finnhub(Resource):

    @classmethod
    def get(cls):
        try:
            args = request.args

            if args is None or args == {}:
                return ResponseAPI.send(status_code=400, message="Please provide request parameters information")
            if args.get('category') and args.get('pair') and \
                    args.get('from') and args.get('to') and args.get('resolution'):

                df = prepaireCandels(args['category'], args['pair'], args['from'], args['to'],
                                     resolution=args['resolution'])

                data = {
                        'close':list(df['close']),
                        'open': list(df['open']),
                        'low':list( df['low']),
                        'high':list( df['high']),
                        'volume':list( df['volume']),
                        'timestamp':list(df['timestamp'])

                    }

                return ResponseAPI.send(status_code=200, message="successful", data=data)

        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent date format!", data=False)
        except :
            return ResponseAPI.send(status_code=422, message="Inconsistent date format!", data=False)
