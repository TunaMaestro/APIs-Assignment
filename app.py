from flask import Flask, request, render_template

import gather_transport_data as td
import graphing
import weather_api

app = Flask(__name__)

weather_definitions = {}
with open('static/weather_definitions.csv') as f:
    for line in f:
        if 'disabled' in line:
            continue
        id, label, metric, imperial = line.strip().split(',')
        weather_definitions[id] = {
            'label': label,
            'units': (metric, imperial)
        }
transport_definitions = {}
with open('static/transport_definitions.csv') as f:
    for line in f:
        line = line.strip().split(',')
        transport_definitions[line[0]] = line[1]

transport = td.read_data()

sumTransport = td.all_transport_sum(td.xs(transport, line="All - NSW"))
sumTransport = td.aggregate(sumTransport, 7)

weather = weather_api.historical_sydney()[['rain', 'temp']]

figJSON = graphing.jsonify(graphing.default_graph(leftFrame=sumTransport, rightFrame=weather,
                                 definitions=weather_definitions))

locations = transport.columns
subLoc = []
for mode, loc in locations:
    if loc not in subLoc:
        subLoc.append(loc)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', graphJSON=figJSON, definitions=weather_definitions, locations=subLoc)


@app.route('/test', methods=['POST'])
def test():
    print('test reception')
    form = dict(request.form)
    if form.get('df') == "false":
        # graphing.default_graph()
        return figJSON
    print(form)

    # print(data)

    if form.get("filter-all") == "true":
        modes = None
    else:
        modes = [transport_definitions[x.split('-')[1]] for x in form if x.startswith("filter") and form[x] == "true"]


    data = td.xs(transport, line=form.get("loc"), modes=modes)

    if form.get("agg") == "aggregated":
        data = td.all_transport_sum(data)

    data = td.aggregate(data, 7)

    fig = graphing.default_graph(data, weather, weather_definitions)
    return graphing.jsonify(fig)


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
