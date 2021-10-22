##-----------------------Dashboard of MarketPredict REST API --------------------------------# 

import dash_core_components as dcc
import dash_html_components as html
from datetime import date




layout = html.Div([
    html.H1('Market Data Plot'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'EURUSD', 'value': 'EURUSD'},
            {'label': 'USDJPY', 'value': 'USDJPY'},
            {'label': 'GBPUSD', 'value': 'GBPUSD'},
            {'label': 'USDCHF', 'value': 'USDCHF'},
            {'label': 'XAUUSD', 'value': 'XAUUSD'},
            {'label': 'BTCUSDT', 'value': 'BTCUSDT'},

        ],
        value='BTCUSDT'
    ),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2020, 8, 5),
        max_date_allowed=date.today(),
        initial_visible_month=date.today(),
        end_date=date.today()
    ),
    dcc.Graph(id='my-graph')
], style={'width': '500'})
