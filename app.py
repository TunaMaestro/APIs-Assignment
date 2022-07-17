from flask import Flask, render_template, request
import weather_api, graphing
import pprint
import datetime
import pandas as pd

app = Flask(__name__)

x = 5

definitions = {}
with open('definitions.csv') as f:
    for line in f:
        id, label, metric, imperial = line.strip().split(',')
        definitions[id] = {
            'label': label,
            'units': (metric, imperial)
        }


@app.route('/', methods=['GET', 'POST'])
def index():
    figJSON = graphing.graph(weather_api.historical_sydney(), ['rain', 'temp'], definitions)

    return render_template('index.html', graphJSON=figJSON)


@app.route('/graphs')
def graphs():
    data = weather_api.process_data()

    data.to_csv('testLogOutput.csv')

    graph = graphing.graph(data, 'speed')
    return render_template('graphs.html', graph=graph)


# @app.route('/reading')
# def reading():
#     return str(datetime.datetime.now().microsecond)


if __name__ == '__main__':
    app.run()
