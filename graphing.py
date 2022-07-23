import json
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import gather_transport_data
import pandas as pd
import weather_api


def default_graph(leftFrame, rightFrame, definitions):
    """
    :param leftFrame: pd.Dataframe of left axis
    :param frame: pd.DataFrame
    :param definitions dict of key to english labels
    :return: plotly graph json
    """

    # https://plotly.com/python/multiple-axes/
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    pd.options.plotting.backend = "plotly"

    labels = {key: definitions[key]['label'] for key in definitions}

    colours = px.colors.qualitative.Plotly
    parts = [
        go.Bar(x=rightFrame.index, y=rightFrame['rain'], base=dict(color=colours[0]),
               name=labels['rain'],
               yaxis=f'y'
               ),

        go.Scatter(x=rightFrame.index, y=rightFrame['temp'], mode='lines', line=dict(color=colours[1]),
                   name=labels['temp'],
                   yaxis=f'y2'
                   )
    ]
    fig.add_traces(parts)
    for i, col in enumerate(['rain', 'temp']):
        fig.update_layout({
            f"yaxis{str() if i == 0 else i + 1}": {
                "title": labels[col],
                "range": [0, round(rightFrame[col].max(), -1) + 10],
                "side": "right",
                "color": colours[i]
                # position=0.1,
                # anchor="free"
            }
        })

    fig.update_layout(dict(
        yaxis1={
            "title_standoff": 40
        },
        paper_bgcolor="rgba(0,0,0,0)"
    )
    )

    # https://maegul.gitbooks.io/resguides-plotly/content/content/plotting_locally_and_offline/python/multiple_axes_and_subplots.html

    fig.update_layout(
        title_text="Double Y Axis Example"
    )
    fig.update_layout(
        xaxis=dict(title_text="Date",
                   domain=[0.05, 0.85])
    )
    #     yaxis=dict(
    #         title="Temperature",
    #         range=[0, 30],
    #         side="right",
    #         # position=0.1,
    #         # anchor="free"
    #     ),
    #     yaxis2=dict(
    #         title="y2",
    #         range=[0, 150],
    #         side="right",
    #         overlaying="y",
    #     )
    # )

    #     yaxis=dict(
    #         title="yaxis1 title",
    #         side="right",
    #         overlaying="y1",
    #         # anchor="free"
    #     ),
    #     yaxis2=dict(
    #         title="yaxis2 title",
    #         side="right",
    #         overlaying="y2",
    #         anchor="free",
    #         position=0
    #     )
    if isinstance(leftFrame, pd.DataFrame):
        traces = [go.Scatter(x=leftFrame.index, y=leftFrame[col], yaxis="y3", name=col) for col in leftFrame.columns]
    else:
        traces = [go.Scatter(x=leftFrame.index, y=leftFrame, yaxis="y3", name="Transport")]

    fig.add_traces(
        traces
    )

    fig.update_layout(
        yaxis3=dict(
            title="Tranposrt Sum",
            side="left",
            overlaying="y"
        )
    )
    # fig2 = px.line(leftFrame)
    # fig2.show()

    if __name__ == '__main__':
        fig.show()
    return fig


def jsonify(fig):
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


# weatherData = weather_api.process_data()
#
# import plotly.graph_objects as go
#
# transportData = gather_transport_data.process_data()
# mode = 'Bus'
# df = transportData[mode]
#
# forHour = df.loc[df.index.hour == 8 & df.index.weekday == 5]
#
# pd.options.plotting.backend = "plotly"
# fig = forHour.plot()
# fig.show()

if __name__ == '__main__':
    definitions = {}
    with open('static/weather_definitions.csv') as f:
        for line in f:
            id, label, metric, imperial = line.strip().split(',')
            definitions[id] = {
                'label': label,
                'units': (metric, imperial)
            }
    transport = gather_transport_data.read_data()
    bus = transport['Bus']
    sumTransport = gather_transport_data.all_transport_sum(transport)
    sumTransport = gather_transport_data.aggregate_over_time(sumTransport)
    default_graph(leftFrame=sumTransport, leftCols=[], rightFrame=weather_api.historical_sydney(),
                  rightCols=['rain', 'temp'],
                  definitions=definitions)


def doThing():
    definitions = {}
    with open('static/weather_definitions.csv') as f:
        for line in f:
            id, label, metric, imperial = line.strip().split(',')
            definitions[id] = {
                'label': label,
                'units': (metric, imperial)
            }
    transport = gather_transport_data.process_data()
    bus = transport['Bus']
    sumTransport = gather_transport_data.all_transport_sum(transport)
    default_graph(leftFrame=sumTransport, leftCols=[], rightFrame=weather_api.historical_sydney(),
                  rightCols=['rain', 'temp'],
                  definitions=definitions)
