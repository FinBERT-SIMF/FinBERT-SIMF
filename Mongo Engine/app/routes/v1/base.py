from flask import Blueprint
from flask_restful import Api
from app.resources.news import News
from app.resources.predict import Predict
from app.resources.candle import Candle
from app.resources.finnhub import Finnhub
from app.resources.plotPrediction import PlotPreiction
from app.resources.concepts import Concepts


BASE_BLUEPRINT = Blueprint("base", __name__)
api = Api(BASE_BLUEPRINT)

#A route for save and get news
api.add_resource(News, "/news")

#A route for get and set prediction
api.add_resource(Predict, "/predict")

# A route for save and get candles from tradingview
api.add_resource(Candle, "/candle")

# A route for fetch candle data from finnhub
api.add_resource(Finnhub, "/finnub")

#dashboard test with rendertemplate and no Dash
api.add_resource(PlotPreiction, "/dashboardTest")

#concepts get and set route
api.add_resource(Concepts, "/concepts")

