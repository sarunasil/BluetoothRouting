import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas
import datetime
import requests

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def fetch_original_alerts():

    timestamps = []

    response = requests.get("http://localhost:8080/alarms")
    if response.status_code != 200:
        return timestamps

    response = response.text
    if response == "":
        return timestamps

    for line in response.split("\n"):
        if line == "":
            continue

        data = line.split(" - ", 2)
        if data[1] != "WARNING":
            continue

        timestamps.append(data[0])

    return timestamps


def update_alerts_graph(timestamps_values):
    original_alerts = fetch_original_alerts()
    for timestamp in original_alerts:
        original_timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
        closest_timestamp = datetime.datetime(year=original_timestamp.year, month=original_timestamp.month, day=original_timestamp.day,
                                              hour=original_timestamp.hour, minute=original_timestamp.minute)

        closest_timestamp = str(closest_timestamp)
        if closest_timestamp in timestamps_values:
            timestamps_values[closest_timestamp] += 1


def update_graph():
    start = datetime.datetime.today().date()
    end = start + datetime.timedelta(days=1)
    start_str = datetime.datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
    end_str = datetime.datetime.strftime(end, "%Y-%m-%d %H:%M:%S")

    timestamps = pandas.date_range(start=start_str, end=end_str, periods=24 * 60 + 1)
    timestamps_values = {str(timestamp): 0 for timestamp in timestamps}
    update_alerts_graph(timestamps_values)

    x_values = list(timestamps_values.keys())
    y_values = list(timestamps_values.values())

    return html.Div(children=[
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': x_values,
                     'y': y_values, 'type': 'scatter'},
                ],
                'layout': {
                    'title': 'Alarm Messages Visualisation',
                    'xaxis': {"range": [start_str, end_str]},
                    'yaxis': {"range": [min(y_values), max(y_values)]}
                }
            }
        )
    ])


app.layout = update_graph

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)