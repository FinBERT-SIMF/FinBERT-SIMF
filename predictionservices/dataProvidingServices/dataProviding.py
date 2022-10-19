# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 19:18:04 2021

@author: Novin
"""
from typing import Tuple

import os
import json
import logging
import time
from collections import deque
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import ta
from sklearn import preprocessing

import errors
from definitions import ROOT_DIR
'''
max_L = 15
SEQ_LEN = 7
embedding_dim = 210
marketDelayWindow = SEQ_LEN * 60 * 60
delayForINdicators = SEQ_LEN * 60 * 60
SEQ_LEN_news = 7

'''

FUTURE_PERIOD_PREDICT = 1
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

def prepare_long_candle_data(category, pair, start_date, end_date, resolution=60) -> pd.DataFrame:
    """Fetch data from finnhub.io api and return it as a pandas DataFrame. Fetch 2 months worth of data

    :param category: currency pair category
    :param pair: symbol
    :param start_date: from timestamp
    :param end_date: to timestamp
    :param resolution: timeframe
    :return: DataFrame
    :exception: DataProvidingException when fail to connect to finnhub
    """
    market_df = pd.DataFrame()
    start_date = int(start_date)
    end_date = int(end_date)
    end = 0
    symbol = ''
    try:
        category = category.lower()
        start = start_date

        if category == "forex":
            symbol = 'OANDA:'
            symbol = symbol + pair[0:3].upper() + '_' + pair[3:].upper()
        elif category == "cryptocurrency":
            symbol = 'BINANCE:'
            if pair.upper().find('BTCUSD') != -1:
                symbol = symbol + 'BTCUSDT'
                category = 'crypto'
        else:
            logging.error(f"{category=} must be either 'forex' or 'cryptocurrency'")
            return

        # two months
        step = 2592000 + 2592000
        while end < end_date:
            end = start + step
            query_string = 'https://finnhub.io/api/v1/' + category.lower() + '/candle?symbol=' + \
                           symbol + '&resolution=' + str(resolution) + '&from='
            query_string += str(start) + '&to=' + str(int(end)) + '&token=bveu6qn48v6rhdtufjbg'

            # print(endDate)

            r = requests.get(query_string)
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
                market_df = pd.concat([market_df, df], ignore_index=True)
                time.sleep(50 / 1000)
                start = end + 3600
            # else:
            #    raise TypeError
        return market_df

    except ConnectionError as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=r.status_code)
    except OSError as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=410)
    except Exception as err:
        raise errors.DataProvidingException(message="Market Data Failed", code=420)


# todo write new function for analysis of news and market data and report preparation

def prepare_candles(category, pair, start_date, end_date, resolution=60, sequence_length=7):
    """Fetch raw technical indicators using finnhub.io API for a time period equal to sequence_length days

    :param category: currency pair category
    :param pair: symbol
    :param start_date: from timestamp
    :param end_date: to timestamp
    :param resolution: timeframe
    :param sequence_length: length of sliding time window
    :return: DataFrame
    :exception: DataProvidingException when fail to connect to finnhub
    """
    # I manually determine the start_date because I itself calculate indicator values
    delay_for_indicators = sequence_length * 60 * 60 * 60
    start_date = int(end_date) - delay_for_indicators
    end_date = int(end_date)

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
        else:
            logging.error(f"{category=} must be either 'forex' or 'cryptocurrency'")
            return

        logging.info(f"{category=}, {symbol=}, {start_date=}, {end_date=}")

        query_string = 'https://finnhub.io/api/v1/' + category.lower() + '/candle?symbol=' + symbol \
                       + '&resolution=' + str(resolution) + '&from='
        query_string += str(start_date) + '&to=' + str(end_date) + '&token=bveu6qn48v6rhdtufjbg'

        logging.info(query_string)

        # columns={'Close','High','Low','Open','Status','timestamp','Volume'}
        r = requests.get(query_string)
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


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute and append technical indicators to raw technical dataframe.

    :param df: input technical indicator data
    :return: augmented pandas DataFrame
    """
    try:
        df = df.drop_duplicates(subset=['timestamp'])

        # df = ta.utils.dropna(df)

        # Initialize Bollinger Bands Indicator
        indicator_bb = ta.volatility.BollingerBands(close=df["Close"], n=20, ndev=2)
        df['bb_bbm'] = indicator_bb.bollinger_mavg()

        df['EMA'] = ta.trend.EMAIndicator(close=df['Close'], n=14, fillna=False).ema_indicator()

        df['on_balance_volume'] = ta.volume.OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume'],
                                                                     fillna=False).on_balance_volume()
        df = df.dropna()
        return df

    except Exception:
        raise errors.DataProvidingException(message="Failed to calculate Market Indicator", code=401)


def to_nearest_hour(ts):
    return ts - (ts % 1800)


def query_market_data(category, pair,
                      start_date, end_date,
                      Long=False, resolution=60, sequence_length=7) -> Tuple[pd.DataFrame, int, int]:
    try:
        if Long:
            '''
            This part of code implemented for using in Training models
            '''
            df = prepare_long_candle_data(category, pair, start_date, end_date, resolution=resolution)
            df = compute_indicators(df)
            start_date = df.iloc[0].timestamp
            end_date = df.iloc[-1].timestamp
            return df, start_date, end_date

        '''
        this part of code implemented for using in prediction of next timestamp
         
        '''
        df = prepare_candles(category, pair, start_date, end_date, resolution=resolution,
                             sequence_length=sequence_length)
        df = compute_indicators(df)
        start_date = df.iloc[-sequence_length].timestamp
        end_date = df.iloc[-1].timestamp
        return df, start_date, end_date

    except errors.DataProvidingException as err:
        raise errors.DataProvidingException(message=err.message)


# query on mongoDB engine
def query_news(category, pair, start_date, end_date, Long=False) -> pd.DataFrame:
    url = 'http://localhost:5000/Robonews/v1/news'

    try:
        # prepare query
        start_date = int(start_date)
        end_date = int(end_date)
        query = {
            'category': category,
            'keywords': pair,
            'from': start_date,
            'to': end_date
        }

        # query the data
        resp = requests.get(url, params=query)
        resp = json.loads(resp.text)
        data = json.loads(resp['data'])

        df = pd.DataFrame(data)
        logging.info(f"Total Number of News: {len(df)=}")
        return df

    except Exception:
        raise errors.DataProvidingException(message="Error in reading News",
                                            code=data['status'])


def load_market_data(category, pair, start_date, end_date, Long,
                     resolution, sequence_length) -> Tuple[pd.DataFrame, int, int]:
    # NOTE: Only possible for Forex, EURUSD, between 2018-09-24T06:00 and 2021-05-04T23:00
    path_to_technical_indicators = os.path.join(ROOT_DIR, "data", "EURUSDHourlyIndicators.xlsx")
    logging.debug(f"Preparing to load market data from {path_to_technical_indicators}")

    # load data from Excel file. technical indicators have already been computed
    market_df = pd.read_excel(path_to_technical_indicators)

    # fetch start and end dates
    start_date, end_date = market_df['Date'][0], market_df['Date'][len(market_df)-1]

    logging.debug(f"Finished loading market data, it is of length {len(market_df)=}")

    return market_df, start_date, end_date

def load_news(category, news_keywords,
              start_date, end_date, Long) -> pd.DataFrame:
    path_to_news = os.path.join(ROOT_DIR, "data", "totalEURUSDnews.xlsx")

    logging.debug(f"Preparing to load news data from {path_to_news=}")

    news_df = pd.read_excel(path_to_news)

    logging.debug(f"Finished loading news data. number of rows {len(news_df)=}")

    return news_df


def load_raw_data(category, pair, start_date, end_date, news_keywords,
                  resolution=60, Long=False, sequence_length=7, query=True):
    try:
        logging.info(f"{query=}")

        fetch_market_data = query_market_data if query else load_market_data
        fetch_news = query_news if query else load_news

        logging.debug(f"Preparing to fetch market data using {fetch_market_data=}")

        market_df, _start_date, _end_date = fetch_market_data(category, pair, start_date, end_date, Long=Long,
                                                              resolution=resolution,
                                                              sequence_length=sequence_length)

        logging.debug("Finished fetching market data")
        logging.debug(f"Preparing to fetch news using {fetch_news=}")

        news_df = fetch_news(category, news_keywords,
                             start_date=_start_date, end_date=_end_date,
                             Long=Long)

        logging.debug("Finished fetching news")

        logging.info(f'Total news for training: {len(news_df)}')

        return market_df, news_df

    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message)


def rolling_window_normalization(market_df, sequence_length):
    sequential_data = []  # this is a list that will CONTAIN the sequences
    prev_days = deque(maxlen=sequence_length)
    for d, row in market_df.iterrows():
        prev_days.append([n for n in row[:-1]])  # store all but the target
        if len(prev_days) == sequence_length:  # make sure we have 10 sequences!
            return True


def to_this_hour(date):
    return date.replace(microsecond=0, second=0, minute=0)


def transform_news_data(news_df: pd.DataFrame) -> pd.DataFrame:
    # fix dates for news data to be compatible with dates for market data
    if not news_df.empty and 'pubDate' in news_df:
        news_df['Date'] = [datetime.strptime(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                             , '%Y-%m-%d %H:%M:%S') for ts in news_df['pubDate']]
        news_df = news_df.drop('pubDate', 1)

    # convert types
    news_df['title'] = news_df['title'].astype(str)
    news_df['articleBody'] = news_df['articleBody'].astype(str)
    news_df['Date'] = pd.to_datetime(news_df['Date'], utc=True)

    news_df = news_df.set_index('Date')
    return news_df


def choose_features(market_df: pd.DataFrame) -> pd.DataFrame:
    # TODO: check what features they are using, might have been only 12
    return (market_df
        .drop("Open", 1)
        .drop("Low", 1)
        .drop("High", 1)
    )


def transform_market_data(market_df, Long, sequence_length):
    logging.debug("Transforming market data")
    logging.debug("Dropping columns Open, Low, and High")

    market_df['Date'] = pd.to_datetime(market_df['Date'], utc=True)
    market_df = market_df.set_index('Date')

    # transform and compute technical indicators for market data
    if 'timestamp' in market_df.columns:
        market_df = market_df.drop('timestamp', 1)

    if not Long:
        market_df = market_df[-sequence_length:]

    # don't need these columns anymore.
    market_df = choose_features(market_df)

    # create target column
    market_df['target'] = market_df['Close'].shift(-FUTURE_PERIOD_PREDICT)

    logging.debug(f"Normalizing non-target columns")
    for col in market_df.columns.drop('target'):  # go through all features
        market_df[col] = market_df[col].astype(float)
        market_df = market_df.replace([np.inf, -np.inf], None)
        market_df[col] = preprocessing.scale(market_df[col].values)  # scale between 0 and 1.

    logging.debug("Dropping NaN rows")
    market_df.dropna(inplace=True)  # cleanup again... jic.

    logging.debug(f"Finished transforming market data\n{market_df.columns=}\n{len(market_df.columns)=}")

    return market_df


def transform_and_align(market_df, news_df, category, pair, Long=False, max_L=15, sequence_length=7):
    try:
        logging.debug("Preparing to align and transform data")

        if market_df.empty or news_df.empty:
            raise ValueError(f"market_df or news_df is None: {market_df=}, {news_df=}")

        logging.debug(f"{market_df.columns=}")

        market_df = transform_market_data(market_df, Long, sequence_length)
        news_df = transform_news_data(news_df)

        for w in news_df.index:
            if w in market_df.index:
                # TODO: here we assume sentiment is in is in news_df. Make sure this holds true
                # TODO: make sure the timestamp formats are compatible between the dataframes
                # TODO: make sure that we *add* scores if we have more than one news article on the same timestamp (hour)
                # add news sentiment per timestamp to the market df
                market_df.loc[w, 'posScore'] = news_df.loc[w, 'Positive']
                market_df.loc[w, 'negScore'] = news_df.loc[w, 'Negative']
                market_df.loc[w, 'neutralScore'] = news_df.loc[w, 'neutral']

            else:
                # If news is published on a non-business day, find the next hour and add this
                # value to the next hour sentiment score
                i = market_df.index.get_loc(w, method='bfill')
                market_df.iloc[i]['posScore'] += news_df.loc[w, 'Positive']
                market_df.iloc[i]['negScore'] += news_df.loc[w, 'Negative']
                market_df.iloc[i]['neutralScore'] += news_df.loc[w, 'neutral']

        # construct sequences of samples, each of length sequence_length
        # TODO: confirm we are not missing samples here: we can make the moverlap by sequence_length-1 but here
        # it seems like we have no overlap at all and thus missing a lot of samples.

        # list of samples
        sequential_data = []

        # if the maxlen is reached an append will also be followed by a pop in the beginning
        prev_days = deque(maxlen=sequence_length)

        for index, (d, row) in enumerate(market_df.iterrows()):
            # store all but the target
            prev_days.append([n for n in row[:-1]])

            if index < sequence_length - 1:  # make sure we have sequences of length sequence_length
                # TODO: check why the close price of one hour is not the same as the opening price the next hour.
                # i.e. what are we actually trying to precict? Now we are predicting the closing price in 7 hours, right?

                sequential_data.append([np.array(prev_days), row[-1], d])

        # TODO: do this step right away instead of using sequential_data
        X = []
        y = []
        da = []
        for seq, target, d in sequential_data:  # going over our new sequential data
            X.append(seq)  # X is the sequences
            y.append(target)  # y is the targets/labels (buys vs sell/notbuy)
            da.append(d)

        return np.array(X), np.array(y), da

    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message)


def load_training_data(category, pair, start_date, end_date,
                       news_keywords, resolution=60, sequence_length=7,
                       training=False, query=True):
    try:
        logging.info(f"{query=}")

        market_df, news_df = load_raw_data(category,
                                           pair, start_date, end_date,
                                           news_keywords,
                                           resolution=resolution,
                                           sequence_length=sequence_length,
                                           Long=training, query=query)

        X_train, y_train, dates = transform_and_align(market_df, news_df,
                                                      category, pair, Long=training,
                                                      sequence_length=sequence_length)

        return X_train, y_train, dates

    except errors.DataProvidingException as er:
        raise errors.DataProvidingException(message=er.message)


def main():
    s = datetime.utcnow().timestamp()
    three_years_ts = 94867200
    e = s - three_years_ts

    load_training_data(category='Forex', pair='EURUSD', news_keywords='EURUSD',
                       start_date=int(e), end_date=int(s), training=True, query=False)

if __name__ == "__main__":
    main()