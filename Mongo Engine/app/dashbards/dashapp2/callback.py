##-----------------------Dashboard of MarketPredict REST API --------------------------------# 

from datetime import datetime as dt

import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output
from app.model.predictModel import PredictModel
import plotly.graph_objects as go


def register_callbacks(dashapp):
    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')
        , Input('my-date-picker-range', 'start_date')])
    def update_graph(selected_dropdown_value, start_date):
        try:
           
            obj = PredictModel()
            df = obj.getCandle(pair=selected_dropdown_value, resolution='H', start=start_date)
            print(df)
            fig = go.Figure(go.Candlestick(
                x=df.date,
                open=df.open,
                high=df.high,
                low=df.low,
                close=df.close
            ))
            
            return fig
        except Exception as err:
            print(err)
            raise ValueError
