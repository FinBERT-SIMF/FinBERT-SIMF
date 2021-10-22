##-----------------------Dashboard of MarketPredict REST API --------------------------------# 

from datetime import datetime
from datetime import date
import time
import requests
from dash.dependencies import Input
from dash.dependencies import Output
import pandas as pd
import plotly.graph_objects as go



# get candle stick data from Finnhub.io
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

    try:
        time.sleep(0.07)
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

        # columns={'Close','High','Low','Open','Status','timestamp','Volume'}
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

            df['date'] = [datetime.strptime(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                            , '%Y-%m-%d %H:%M:%S') for ts in df['timestamp']]

            return df
        else:
            raise ValueError
    except ConnectionError as err:
        return False
    except OSError as err:
        return False
    except Exception as err:
        return False


def register_callbacks(dashapp):
    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')
        , Input('my-date-picker-range', 'start_date')])
    def update_graph(pair, start_date='2021-1-1'):
        try:
            if start_date is None:
                start_date = '2021-1-1'

            start_date = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())

            endDate = int(datetime.utcnow().timestamp())
            if pair.find('BTCUSDT') != -1:
                category = "Cryptocurrency"
            else :
                category = 'Forex'

            df = prepaireCandels(category=category, pair=pair, startDate=start_date, endDate=endDate)

            fig = go.Figure(go.Candlestick(
                x=df.date,
                open=df.open,
                high=df.high,
                low=df.low,
                close=df.close
            ))
            
            return fig

        except ValueError:
            return False
        except :
            return False
