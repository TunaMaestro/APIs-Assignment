from flask import Flask, render_template

import gather_transport_data as td
import graphing
import weather_api

app = Flask(__name__)

x = 5

definitions = {}
with open('static/definitions.csv') as f:
    for line in f:
        id, label, metric, imperial = line.strip().split(',')
        definitions[id] = {
            'label': label,
            'units': (metric, imperial)
        }


@app.route('/', methods=['GET', 'POST'])
def index():
    transport = td.read_data()

    sumTransport = td.all_transport_sum(transport)
    sumTransport = td.aggregate(sumTransport, 7)
    figJSON = graphing.graph(leftFrame=sumTransport, leftCols=[], rightFrame=weather_api.historical_sydney(), rightCols=['rain', 'temp'],
                                 definitions=definitions)

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
    app.run(port=5001)
