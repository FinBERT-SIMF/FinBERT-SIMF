from flask_restful import Resource
from flask import request,make_response
from flask import Flask, render_template
from app.model.get_graph_html import get_graph


class ChartPlot(Resource):
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
            result = get_graph(search, start)
            if result:
                headers = {'Content-Type': 'text/html'}
                return make_response(render_template('stock_test.html'), 200, headers)

            else:
                headers = {'Content-Type': 'text/html'}
                return make_response(render_template('stock_test.html',sign='notfound'), 200, headers)

        except Exception as e:
            headers = {'Content-Type': 'text/html'}
            return make_response(render_template('main.html', sign=e), 400, headers)