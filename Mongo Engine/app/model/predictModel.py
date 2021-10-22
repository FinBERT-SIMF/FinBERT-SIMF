##-----------------------Prediction Model for saving and responding get requests in MarketPredict REST API--------------------------------# 

from dotenv import load_dotenv
import numpy as np
import os, pathlib
from pymongo import MongoClient
import logging as log
import pymongo
import pandas as pd
from datetime import datetime
import plotly.offline as po
import plotly.graph_objs as go
from flask import Markup

load_dotenv("../.env", verbose=True)


class PredictModel:

    def __init__(self, ):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')
        database_URL = os.environ.get("DATABASE_URL")
        self.client = MongoClient(database_URL)  # When only Mongo DB is running on Docker.
       
        database = os.environ.get("DATABASE_NAME")
        collection = os.environ.get("PREDICT_COLLECTION")
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.outputStandard = ['timestamp', 'pair', 'predictedPrice', 'trend', 'chenge']

    def save_to_DB(self, data):
        log.info('Writing Data to DB')
        try:
            response = self.collection.insert_one(data)
            return response.inserted_id

        except Exception:

            log.info('DataBase Error')
            print(Exception)
            return False

    # check wether a timestapm exists or not
    def find_by_timestamp(self, ts, pair):
        query = {'timestamp': ts, 'pair': pair}
        mydoc = self.collection.find(query)
        exist = len(list(mydoc))
        return exist

    def getPredictedPrice(self, timestamp, pair, resolution, category):
        queryString = {"timestamp": int(timestamp), "pair": pair}  # , "category": category ,'resolution':resolution }
        print("sAEEDE2")
        mydoc = self.collection.find(queryString)
        output = list(mydoc)
        if len(output):
            output = [{item: data[item] for item in data if item != '_id'} for data in output]
            return output[-1]
        else:
            return {"predictedPrice": 0, "trend": "none", "change": 0}

    def validatData(self, data):
        print(data)
        if data['category'].lower() not in ["forex", 'cryptocurrency', 'commodity']:
            raise ValueError("Invalid data type for category!")
        # todo : update pairs list
        # if data['pair'].lower() not in ["eurusd", "USDJPY", "GBPUSD", "BTCUSDT",'USDCHF']:
        #   raise ValueError("Invalid data type for pair!")
        elif int(data['timestamp']) < 0:
            raise ValueError("Invalid Unix UTC Timestamp")
        elif self.find_by_timestamp(data['timestamp'], data['pair']):
            raise ValueError("Duplicated Timestamp")
        else:
            current = datetime.now().timestamp()
            data['createdat'] = int(current)
            return data
        return False

    def find_by_date_pair_category(self, pair, timestamp, category):
        try:
            print('test')
            log.info('find news with particular publishing timestamp and keywords')

            self.collection.create_index([('pair', pymongo.ASCENDING),
                                          ('category', pymongo.ASCENDING),
                                          ('timestamp', pymongo.ASCENDING)],
                                         name='pubDate_category_keywords')
            log.info(self.collection.index_information())

            queryString = {"timestamp": {"$lte": timestamp}, "pair": pair, "category": category}
            prediction = self.collection.find(queryString)

            priceList = []
            changeList = []
            tsList = []
            trendList = []

            for item in list(prediction):
                priceList.append(item['predictedPrice'])
                tsList.append(int(item['timestamp']))

                if 'trend' in item.keys():
                    trendList.append(item['trend'])
                    changeList.append(item['change'])
                else:
                    trendList.append('none')
                    changeList.append(0)
            print(1)
            output = {
                'predictedPrice': priceList,
                'trend': trendList,
                'change': changeList,
                'timestamp': tsList
            }

            self.collection.drop_indexes()
            print(output)
            return output
        except Exception:
            print(Exception)
            return False

    def find_by_date_symbol_resolution(self, symbol, start, end, resolution):
        try:

            self.collection.create_index([('pair', pymongo.ASCENDING),
                                          ('category', pymongo.ASCENDING),
                                          ('timestamp', pymongo.ASCENDING)],
                                         name='timestamp_resolution_symbol')
            log.info(self.collection.index_information())

            queryString = {"timestamp": {"$gte": int(start), "$lte": int(end)}, "pair": symbol
                           }
            candles = self.collection.find(queryString)

            priceList = []
            changeList = []
            tsList = []
            trendList = []

            for item in list(candles):
                priceList.append(item['predictedPrice'])
                tsList.append(int(item['timestamp']))
                if 'trend' in item.keys():
                    trendList.append(item['trend'])
                    changeList.append(item['change'])
                else:
                    trendList.append('none')
                    changeList.append(0)
            output = {
                'predictedPrice': priceList,
                'trend': trendList,
                'change': changeList,
                'timestamp': tsList
            }

            self.collection.drop_indexes()
            print(output)
            return output
        except Exception:
            print(Exception)
            return False

    def find_by_pair(self, pair):
        log.info('find news with particular keywords')
        matchstring = {"keywords": pair}
        prediction = self.collection.find(matchstring)
        output = [{item: data[item] for item in data if item != '_id'} for data in prediction]
        return output

    def get_graph(self, search, start):
        try:
            sid = search
            sd = start
            df = self.getCandle(pair=search, resolution='H', start=sd)

            print(df)

            if df is not None:
                print("df ok")
                SMA5 = df['close'].rolling(5).mean()
                SMA10 = df['close'].rolling(10).mean()
                SMA20 = df['close'].rolling(20).mean()
                SMA60 = df['close'].rolling(60).mean()
                trace = go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                                       name='K')
                # s5 = go.Scatter(x=SMA5.index, y=SMA5.values, name='5MA')
                # s10 = go.Scatter(x=SMA10.index, y=SMA10.values, name='10MA')
                # s20 = go.Scatter(x=SMA20.index, y=SMA20.values, name='20MA')
                s60 = go.Scatter(x=df.index, y=df['close'], name='60MA', mode="lines+markers")
                # data = [trace, s5, s10, s20, s60]
                data = [s60]
                layout = {'title': sid}
                fig = dict(data=data, layout=layout)
                path = str(pathlib.Path().absolute()) + "/templates/stock.html"
                print(path)
                po.plot(fig, filename='templates/stock.html', auto_open=False)
                return True
            else:
                return False
        except:
            return False

    def get_quantile(self, close):
        try:

            c1 = close
            c2 = c1[1:]
            c2 = np.append(c2, c2[-1:])

            arr = c2 - c1
            arr = arr[~np.isnan(arr)]
            positiveChanges = [w for w in arr if w > 0]
            negativeChanges = [w for w in arr if w <= 0]
            positiveBounderies = [np.quantile(positiveChanges, 0.1),
                                  np.quantile(positiveChanges, 0.3),
                                  np.quantile(positiveChanges, 0.5),
                                  np.quantile(positiveChanges, 0.7),
                                  np.quantile(positiveChanges, 0.9)]
            negativeBounderies = [np.quantile(negativeChanges, 0.1),
                                  np.quantile(negativeChanges, 0.3),
                                  np.quantile(negativeChanges, 0.5),
                                  np.quantile(negativeChanges, 0.7),
                                  np.quantile(negativeChanges, 0.9)]
            return positiveBounderies, np.sort(np.absolute(negativeBounderies))

        except Exception as err:
            print(str(err))
            return False

    def getCandle(self, pair, resolution, start):
        try:
            print(type(start))
            print(start)
            start = datetime.strptime(start, '%Y-%m-%d')
            ts = start.timestamp()
            print(ts)
            # fix start to 10 dayes ago from now

            ts2 = int(datetime.utcnow().timestamp())
            ts2 = ts2 - (ts2 % 3600)  # round to nearest hour
            end = ts2 + 3600
            data = self.find_by_date_symbol_resolution(symbol=pair, start=int(ts), end=int(end),
                                                       resolution=resolution)

            length = len(data['trend'])

            # convert prediction to candles
            closeList = np.zeros(length)
            openList = np.zeros(length)
            lowList = np.zeros(length)
            highList = np.zeros(length)
            dateList = []
            posBond, negBond = self.get_quantile(np.array(data['predictedPrice']))
            print(posBond)
            print(negBond)
            k = 0
            for candle, i in zip(data['trend'], range(len(data['trend']))):
                change = data['change'][i]
                if candle == 'up':
                    j = 0
                    while j < len(negBond) and data['change'][i] > posBond[j]:
                        j = j + 1
                    j = j + 1
                    print(data['change'][i], j)
                    closeList[k] = np.float64(data['predictedPrice'][i])
                    openList[k] = data['predictedPrice'][i] - (2* j  / 100 * data['predictedPrice'][i])
                    lowList[k] = data['predictedPrice'][i]
                    highList[k] = data['predictedPrice'][i]
                    dateList.append(datetime.fromtimestamp(data['timestamp'][i]))
                    k = k + 1

                else:
                    j = 0
                    while j < len(negBond) and abs(data['change'][i]) > negBond[j]:
                        j = j + 1
                    j = j + 1
                    closeList[k] = data['predictedPrice'][i]
                    openList[k] = data['predictedPrice'][i] + (2* j / 100 * data['predictedPrice'][i])
                    lowList[k] = data['predictedPrice'][i]
                    highList[k] = data['predictedPrice'][i]
                    dateList.append(datetime.fromtimestamp(data['timestamp'][i]))
                    k = k + 1
            df = pd.DataFrame(data={'date': dateList,
                                    'close': closeList,
                                    'open': openList,
                                    'low': lowList,
                                    'high': highList}

                              )

            return df

        except Exception:
            print("Error in prediction data providing!")
            return None
