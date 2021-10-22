from flask_restful import Resource
from flask import request,make_response
from flask import Flask, render_template
from app.model.predictModel import PredictModel
import time,os
from app import app
import pathlib,jinja2

'''
A test route for plot charts of prediction with HTML and render template without DASH.
A majr prblem was the server cacheing of chart.
'''
class PlotPreiction(Resource):
    @classmethod
    def get(cls):
        try:
            headers = {'Content-Type': 'text/html'}
            return make_response(render_template('main.html'), 200, headers)
            #return render_template('test.html')
        except Exception as e:
            headers = {'Content-Type': 'text/html'}
            return make_response(render_template('main.html',sign=e), 400, headers)

    @classmethod
    def post(cls):
        try:
            search = request.form['search']
            start = request.form['start']
            obj = PredictModel()
            jinja2.clear_caches()
            Result = obj.get_graph(search=search, start=start)

            if Result:

                headers = {'Content-Type': 'text/html',
                           'Cache-Control': 'max-age=0'}
                return make_response(render_template('stock.html' ), 200, headers)


            else:
                headers = {'Content-Type': 'text/html',
                           'Cache-Control': 'max-age=0'}
                return make_response(render_template('stock.html',sign='notfound'), 200, headers)

        except Exception as e:
            headers = {'Content-Type': 'text/html'}
            return make_response(render_template('main.html', sign=e), 400, headers)