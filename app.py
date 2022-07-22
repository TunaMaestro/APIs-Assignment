from flask import Flask, request, render_template

import gather_transport_data as td
import graphing
import weather_api

app = Flask(__name__)

definitions = {}
with open('static/definitions.csv') as f:
    for line in f:
        if 'disabled' in line:
            continue
        id, label, metric, imperial = line.strip().split(',')
        definitions[id] = {
            'label': label,
            'units': (metric, imperial)
        }

transport = td.read_data()

sumTransport = td.all_transport_sum(td.xs(transport, line="All - NSW"))
sumTransport = td.aggregate(sumTransport, 7)
figJSON = graphing.default_graph(leftFrame=sumTransport, leftCols=[], rightFrame=weather_api.historical_sydney(),
                                 rightCols=['rain', 'temp'],
                                 definitions=definitions)

locations = transport.columns
subLoc = []
for mode, loc in locations:
    if loc not in subLoc:
        subLoc.append(loc)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', graphJSON=figJSON, definitions=definitions, locations=subLoc)


@app.route('/test', methods=['POST'])
def test():
    print('test reception')
    form = dict(request.form)
    if form.get('df') == "false":
        # graphing.default_graph()
        return figJSON
    print(form)

    data = td.xs(transport, line=form.get('loc'))

    print(data)

    return str(data)





@app.route('/graphs')
def graphs():
    data = weather_api.process_data()

    data.to_csv('testLogOutput.csv')

    graph = graphing.default_graph(data, 'speed')
    return render_template('graphs.html', graph=graph)


# @app.route('/reading')
# def reading():
#     return str(datetime.datetime.now().microsecond)


if __name__ == '__main__':
    app.run(port=5001)
