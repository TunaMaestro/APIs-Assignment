import requests
import os
import urllib.parse
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import json
import datetime
import math

pd.options.plotting.backend = "plotly"

dataLoc = "dynamic/weather/"

def call_api(path, query, endpoint=f'https://api.openweathermap.org'):
    url = f'{endpoint}{path}{query}'
    print(url)
    return requests.request('get', url).json()


def weather_from_coords(lat, lon):
    key = os.environ['WEATHER_HISTORY_KEY']
    units = "metric"
    count = 0
    path = f'/data/2.5/history/city'
    start = int(datetime.datetime(year=2020, month=1, day=1, hour=1).timestamp())
    start = int((datetime.datetime.now() - datetime.timedelta(days=363)).timestamp())
    end = int(datetime.datetime.now().timestamp())
    query = f'?lat={lat}&lon={lon}&units={units}&type=hour&appid={key}&start={start}&end={end}'
    return call_api(path, query, endpoint="https://history.openweathermap.org")


def historical_one_year(city, downloadNew=False):
    list = []
    with open(f'{dataLoc}staticWeatherFrom2020.json') as f:
        keysToKeep = ['dt', 'main', 'weather', 'clouds', 'wind']
        for i in json.load(f):
            list.append({key: val for key, val in i.items() if key in keysToKeep})

    if downloadNew:
        key = os.environ['WEATHER_HISTORY_KEY']
        units = 'metric'
        count = 168  # Max one week per request as per https://openweathermap.org/history
        path = '/data/2.5/history/city'
        start = datetime.datetime.now() - datetime.timedelta(days=364)
        # start = datetime.datetime.now() - datetime.timedelta(days=28)
        while start < datetime.datetime.now() - datetime.timedelta(days=1):
            dt = int(start.timestamp())
            query = f'?city={city}&units={units}&type=hour&appid={key}&start={dt}&cnt={count}'
            response = call_api(path, query, endpoint="https://history.openweathermap.org")
            list.extend(response['list'])
            print(start.isoformat())
            start += datetime.timedelta(weeks=1)
        with open('learning files/rawPastYear.txt', 'w') as f:
            json.dump(list, f)
    with open('learning files/rawPastYear.txt') as f:
        list.extend(json.load(f))
    return list


def city_data(city, country='AU'):
    city = urllib.parse.quote(city)
    key = os.environ['WEATHER_HISTORY_KEY']
    path = f'/geo/1.0/direct'
    query = f'?q={city}&limit=1&appid={key}'
    # print(path, query)
    return call_api(path, query)


# def temperature(data):
#     temps = {}
#     for weatherData in data['list']:
#         temps[weatherData['dt']] = weatherData['main']['temp']
#     return temps


def process_data(data=None):
    pd.set_option('display.max_columns', 4)
    if data is None:
        with open('learning files/testData.json') as f:
            data = json.load(f)['list']

    for i, val in enumerate(data):
        data[i]['dt'] = datetime.datetime.fromtimestamp(data[i]['dt'])
    weatherData = [x['main'] for x in data]
    weatherDF = pd.DataFrame(weatherData)
    windData = [x['wind'] for x in data]
    windDF = pd.DataFrame(windData)
    data = pd.DataFrame(data=data)
    flattenRain = lambda x: x if isinstance(x, float) else x['1h']
    data['rain'] = data['rain'].map(flattenRain)
    final = pd.concat([data, weatherDF, windDF], axis=1)
    final = final.set_index('dt')

    aggregatePeriod = 7  # in days
    def match_time_period(dt):
        return dt.timestamp() // datetime.timedelta(days=aggregatePeriod).total_seconds()

    grouped = final.groupby(by=match_time_period, group_keys=False)

    final = grouped.agg({'temp': np.mean, 'rain': lambda x: np.sum(x)})

    newIndex = [datetime.datetime.fromtimestamp(x * datetime.timedelta(days=aggregatePeriod).total_seconds()) for x in final.index]
    final.index = newIndex

    return final



def historical_sydney():
    """
    :return: pd.DataFrame
    """
    rawList = historical_one_year('Sydney')
    return process_data(rawList)


if __name__ == '__main__':
    # weather_from_city('Sydney', weather_from_coords)
    # data = process_data()
    rawList = historical_one_year('sydney', downloadNew=True)
    # data = process_data(rawList)
    pass
