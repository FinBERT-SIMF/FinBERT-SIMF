# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 19:18:04 2021

@author: Novin
"""
import requests
from datetime import datetime
import pandas as pd
import ta
import json
import numpy as np
from sklearn import preprocessing
import time
from datetime import timedelta
from collections import deque

'''
max_L = 15
SEQ_LEN = 7
embedding_dim = 210
marketDelayWindow = SEQ_LEN * 60 * 60
delayForINdicators = SEQ_LEN * 60 * 60
SEQ_LEN_news = 7

'''
# todo : exception handling ; Done but need revision
import logging as log
import predictionservices.errors as errors

FUTURE_PERIOD_PREDICT = 1


def prepaireLongCandleData(category, pair, startDate, endDate, resolution=60):
    '''
    :param category: currency pair category
    :param pair: symbol
    :param startDate: from timestamp
    :param endDate: to timestamp
    :param resolution: timeframe
    :return: DataFrame
    :exception: DataProvidingException when fail to connect to finnhub
    '''
    marketDF = pd.DataFrame()
    startDate = int(startDate)
    endDate = int(endDate)
    end = 0
    try:

        start = int(startDate)
        if category.lower() == "forex":
            symbol = 'OANDA:'
            symbol = symbol + pair[0:3].upper() + '_' + pair[3:].upper()
        elif category.lower() == "cryptocurrency":
            symbol = 'BINANCE:'
            if pair.upper().find('BTCUSD') != -1:
                symbol = symbol + 'BTCUSDT'
                category = 'crypto'

        # todo : change the incremental value 259200 . Done!
        # two month
        step = 2592000 + 2592000
        # done: change the incremental value 259200

        while (end < endDate):

            end = start + step
            queryString = 'https://finnhub.io/api/v1/' + category.lower() + '/candle?symbol=' + \
                          symbol + '&resolution=' + str(resolution) + '&from='
            queryString += str(start) + '&to=' + str(int(end)) + '&token=bveu6qn48v6rhdtufjbg'

            # print(endDate)

            r = requests.get(queryString)
            if r.status_code == 200 and r.json() is not None:
                df = pd.DataFrame(r.json())

                df['Close'] = df['c']
                df = df.drop('c', 1)

                df['Open'] = df['o']
                df = df.drop('o', 1)

                df['Low'] = df['l']
                df = df.drop('l', 1)

                df['High'] = df['h']
                df = df.drop('h', 1)

                df = df.drop('s', 1)

                df['timestamp'] = df['t']
                df = df.drop('t', 1)

                df['Volume'] = df['v']
                df = df.drop('v', 1)

                df['Date'] = [datetime.strptime(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                                , '%Y-%m-%d %H:%M:%S') for ts in
                              df['timestamp']]
                # df = df.drop('timestamp', 1)
                marketDF = pd.concat([marketDF, df], ignore_index=True)
                time.sleep(50 / 1000)
                start = end + 3600
            # else:
            #    raise TypeError
        return marketDF

    except ConnectionError as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=r.status_code)
    except OSError as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=410)
    except Exception as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=420)


# todo write new function for analysis of news and market data and report preparation

def prepaireCandels(category, pair, startDate, endDate, resolution=60, SEQ_LEN=7):
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
    delayForINdicators = SEQ_LEN * 60 * 60 * 60
    startDate = int(endDate) - delayForINdicators
    endDate = int(endDate)
    # endDate = int(endDate)
    try:
        # todo : for other currency pair
        #  in cryptocurrency format i must update symbol variable
        if category.lower() == "forex":
            symbol = 'OANDA:'
            symbol = symbol + pair[0:3].upper() + '_' + pair[3:].upper()
        elif category.lower() == "cryptocurrency":
            symbol = 'BINANCE:'
            if pair.upper().find('BTCUSD') != -1:
                symbol = symbol + 'BTCUSDT'
            category = 'crypto'

        # print(endDate)
        queryString = 'https://finnhub.io/api/v1/' + category.lower() + '/candle?symbol=' + symbol \
                      + '&resolution=' + str(resolution) + '&from='
        queryString += str(startDate) + '&to=' + str(endDate) + '&token=bveu6qn48v6rhdtufjbg'

        print(queryString)

        # columns={'Close','High','Low','Open','Status','timestamp','Volume'}
        r = requests.get(queryString)
        if r.status_code == 200 and r.json() is not None:
            df = pd.DataFrame(r.json())

            df['Close'] = df['c']
            df = df.drop('c', 1)

            df['Open'] = df['o']
            df = df.drop('o', 1)

            df['Low'] = df['l']
            df = df.drop('l', 1)

            df['High'] = df['h']
            df = df.drop('h', 1)

            df = df.drop('s', 1)

            df['timestamp'] = df['t']
            df = df.drop('t', 1)

            df['Volume'] = df['v']
            df = df.drop('v', 1)

            df['Date'] = [datetime.strptime(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                            , '%Y-%m-%d %H:%M:%S') for ts in df['timestamp']]

            # df = df.drop('timestamp', 1)

            return df
    except ConnectionError as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=r.status_code)
    except OSError as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=410)
    except Exception as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=420)


# indicators selected Based on MUtual information and LSTM weighting
def IndicatorsAddition(df):
    try:

        df = df.drop_duplicates(subset=['timestamp'])

        # df = ta.utils.dropna(df)
        # Initialize Bollinger Bands Indicator
        indicator_bb = ta.volatility.BollingerBands(close=df["Close"], n=20, ndev=2)

        df['EMA'] = ta.trend.EMAIndicator(close=df['Close'], n=14, fillna=False).ema_indicator()

        df['on_balance_volume'] = ta.volume.OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume'],
                                                                     fillna=False).on_balance_volume()
        df['bb_bbm'] = indicator_bb.bollinger_mavg()
        df = df.dropna()
        return df
    except Exception:
        raise errors.DataProvidingException(message="Faild to calculate Market Indicator"
                                            , code=401)


def roundTimestampToNearHour(ts):
    return ts - (ts % 1800)


def prepaireMARKETdata(category: object, pair: object, startDate: object, endDate: object, Long: object = 'False',
                       resolution: object = 60, SEQ_LEN: object = 7, ) -> object:
    try:

        if not Long:
            '''
             this part of code implemented for using in prediction of next timestamp
             
            '''
            df = prepaireCandels(category, pair, startDate, endDate, resolution=resolution, SEQ_LEN=SEQ_LEN)
            df = IndicatorsAddition(df)
            startDate = df.iloc[-SEQ_LEN].timestamp
            endDate = df.iloc[-1].timestamp

            return df, startDate, endDate
        else:
            '''
            This part of code implemented for using in Training models

            '''
            df = prepaireLongCandleData(category, pair, startDate, endDate, resolution=resolution)
            df = IndicatorsAddition(df)
            startDate = df.iloc[0].timestamp
            endDate = df.iloc[-1].timestamp
            return df, startDate, endDate
    except errors.DataProvidingException as err:
        raise errors.DataProvidingException(message=err.message)


# query on mongoDB engine
def prepaireNews(category, pair, startDate, endDate, provider=['fxstreet'], Long=False, ):

    url = 'http://localhost:5000/Robonews/v1/news'
    # todo: add provider for query on news dataset
    # if Long:
    #    startDate = int(endDate) - (SEQ_LEN_news * 60 * 60)
    # else:
    try:
        startDate = int(startDate)
        endDate = int(endDate)
        query = {'category': category,
                 'keywords': pair,
                 'from': startDate,
                 'to': endDate
                 }

        resp = requests.get(url, params=query)
        resp = json.loads(resp.text)
        data = json.loads(resp['data'])
        df = pd.DataFrame(data)
        print("Total Number of News:")
        print(len(df))
        return df
    except Exception:
        raise errors.DataProvidingException(message="Error in reading News",
                                            code=data['status'])


def data_collection_service_for_prediction(category, pair, startDate, endDate, newsKeywords,
                                           provider=['fxstreet'],
                                           resolution=60, Long=False,  SEQ_LEN=7):
    try:

        marketDF, s, e = prepaireMARKETdata(category, pair, startDate, endDate, Long=Long,
                                            resolution=resolution,
                                            SEQ_LEN=SEQ_LEN)
        if not Long:

            newsDF = prepaireNews(category, newsKeywords, startDate=s, endDate=e, provider=provider, Long=Long )
        else:
            newsDF = prepaireNews(category, newsKeywords, s, e, provider=provider, Long=Long)
            print('Total news for training:')
            print(len(newsDF))

        return marketDF, newsDF
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message)
    except Exception:
        raise errors.DataProvidingException(message="Irregular Error", code=500)


# todo : rolling Window Normalization
def rollingWindowNormalization(marketDF, SEQ_LEN):
    sequential_data = []  # this is a list that will CONTAIN the sequences
    prev_days = deque(maxlen=SEQ_LEN)
    for d, row in marketDF.iterrows():
        # todo: set index for two dataframes. DONE!
        prev_days.append([n for n in row[:-1]])  # store all but the target
        if len(prev_days) == SEQ_LEN:  # make sure we have 10 sequences!
            return True


def marketDataTransformation(marketDf, long=False):
    try:
        marketDf = marketDf.drop("High", 1)  # don't need this anymore.
        marketDf = marketDf.drop("Low", 1)  # don't need this anymore.
        marketDf = marketDf.drop("Open", 1)  # don't need this anymore.
        marketDf['target'] = marketDf['Close'].shift(-FUTURE_PERIOD_PREDICT)
        for col in marketDf.columns:  # go through all of the columns
            if col != "target":  # normalize all ... except for the target itself!
                marketDf[col] = [float(e) for e in marketDf[col]]
                marketDf = marketDf.replace([np.inf, -np.inf], None)
                marketDf[col] = preprocessing.scale(marketDf[col].values)  # scale between 0 and 1.

        marketDf.dropna(inplace=True)  # cleanup again... jic.
        return marketDf
    except:
        raise errors.DataProvidingException(message="Error in Normalization", code=500)



def dataAlighnment(marketDF, newsDF, category, pair, Long=False, max_L=15,  SEQ_LEN=7):
    try:
        if len(marketDF) == 0:
            raise ValueError
        marketDF = marketDF.drop('timestamp', 1)
        marketDF = marketDF.set_index('Date')
        marketDF = marketDataTransformation(marketDF, long=Long)
        if not Long:
            marketDF = marketDF[-SEQ_LEN:]

        aligned_news_data = []
        if len(newsDF) != 0:
            newsDF['Date'] = [datetime.strptime(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                                , '%Y-%m-%d %H:%M:%S') for ts in newsDF['pubDate']]

            newsDF = newsDF.drop('pubDate', 1)
            newsDF = newsDF.set_index('Date')


        for w in newsDF.index:
            if w in marketDF.index:
                marketDF.loc[w, 'posScore'] = newsDF.loc[w, 'Positive']
                marketDF.loc[w, 'negScore'] = newsDF.loc[w, 'Negative']
                marketDF.loc[w, 'neutralScore'] = newsDF.loc[w, 'neutral']

            else:
                # News published in non bussiness days , find next hour and add this values to the next hour senScore
                i = marketDF.index.get_loc(w, method='bfill')
                marketDF.iloc[i]['posScore'] += newsDF.loc[w, 'Positive']
                marketDF.iloc[i]['negScore'] += newsDF.loc[w, 'Negative']
                marketDF.iloc[i]['neutralScore'] += newsDF.loc[w, 'neutral']


        sequential_data = []  # this is a list that will CONTAIN the sequences
        prev_days = deque(maxlen=SEQ_LEN)
        for d, row in marketDF.iterrows():

            prev_days.append([n for n in row[:-1]])  # store all but the target
            if len(prev_days) == SEQ_LEN:  # make sure we have 10 sequences!
                sequential_data.append([np.array(prev_days), row[-1], d])
        X = []
        y = []
        da = []

        for seq, target, d in sequential_data:  # going over our new sequential data
            X.append(seq)  # X is the sequences
            y.append(target)  # y is the targets/labels (buys vs sell/notbuy)
            da.append(d)


        return np.array(X), np.array(y),da
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message)



def prepairDataForLoad(category, pair, startDate, endDate, newsKeywords,
                       provider=['fxstreet'],
                       resolution=60, SEQ_LEN=7,
                       Training=False, conceptsType='pair'):
    try:

        if Training:
            marketDF, newsDF = data_collection_service_for_prediction(category,
                                                                      pair, startDate, endDate
                                                                      , newsKeywords,
                                                                      provider=provider,
                                                                      resolution=resolution, SEQ_LEN=SEQ_LEN,
                                                                      Long=True)

            X_train, Y_train, news_train, dates = dataAlighnment(marketDF, newsDF,
                                                                 category, pair, Long=True,
                                                                 SEQ_LEN=SEQ_LEN )


        else:
            marketDF, newsDF = data_collection_service_for_prediction(category,
                                                                      pair, startDate, endDate
                                                                      , newsKeywords,
                                                                      provider=provider,
                                                                      resolution=resolution, SEQ_LEN=SEQ_LEN,
                                                                      Long=False, )
            X_train, Y_train, dates = dataAlighnment(marketDF, newsDF, category, pair
                                                                 , Long=False, SEQ_LEN=SEQ_LEN )
        return X_train, Y_train, dates
    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message)
    except:
        raise errors.DataProvidingException(message='Invalid parameters', code=500)


def main():
    s = datetime.utcnow().timestamp()
    threeYearsTS = 94867200
    e = s - threeYearsTS
    prepairDataForLoad(category='Forex', pair='EURUSD', startDate=int(e), endDate=int(s), Training=True)
    return


if __name__ == "__main__":
    main()
