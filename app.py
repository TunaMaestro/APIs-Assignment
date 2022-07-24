from flask import Flask, request, render_template

import gather_transport_data as td
import graphing
import weather_api
import pandas as pd

app = Flask(__name__)

td.request_files()

pd.set_option('display.max_columns', 4)
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

weather = weather_api.historical_sydney()

figJSON = graphing.jsonify(
    graphing.default_graph(leftFrame=td.aggregate(sumTransport, 7), rightFrame=weather[['rain', 'temp']],
                           definitions=weather_definitions))

locations = transport.columns

boxPlots = graphing.box_plot_sliders(td.aggregate(sumTransport, 1))
boxJSON = graphing.jsonify(boxPlots)
subLoc = []
for mode, loc in locations:
    if loc not in subLoc:
        subLoc.append(loc)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', graphJSON=figJSON, secondGraph=boxJSON, definitions=weather_definitions,
                           locations=subLoc,
                           overflow="overflow-hidden",
                           title="Weather and Transport",
                           header="Weather and Transport",
                           page="index")


@app.route('/about')
def about():
    return render_template("about.html", overflow="", title="About the Data", header="About the Data", page="about")


@app.route('/tapping')
def tapping():
    data = td.process_tap_versus()
    fig = graphing.tap_compare(data)
    tapJSON = graphing.jsonify(fig)
    return render_template("tappings.html", tapJSON=tapJSON, overflow="", title="Tapping Data",
                           header="Tap On and Off Comparison",
                           page="tapping")


@app.route('/update_graphs', methods=['POST'])
def update_graphs():
    form = dict(request.form)

    print(form)

    if form.get("filter-all") == "true":
        modes = None
    else:
        modes = [transport_definitions[x.split('-')[1]] for x in form if x.startswith("filter") and form[x] == "true"]

    data = td.xs(transport, line=form.get("loc"), modes=modes)
    print('Selected modes:', modes)
    boxPlot = graphing.box_plot_sliders(td.aggregate(td.all_transport_sum(data), 1))
    boxJSON = graphing.jsonify(boxPlot)

    if form.get("agg") == "aggregated":
        data = td.all_transport_sum(data)

    data = td.aggregate(data, 7)

    fig = graphing.default_graph(data, weather, weather_definitions)
    figJSON = graphing.jsonify(fig)
    return f'[{figJSON}, {boxJSON}]'


if __name__ == '__main__':
    app.run()
