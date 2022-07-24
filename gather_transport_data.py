import _pickle as pickle
import datetime

import humanize
import numpy as np
import pandas as pd
import requests

dataLoc = "./dynamic/transport/"


def generate_end_urls(start=None):
    if start is None:
        start = datetime.date(2020, 1, 1)
    urls = []
    dates_strings = []
    path = "https://tfnsw-prod-opendata-tpa.s3-ap-southeast-2.amazonaws.com/Opal_Patronage/"
    prefix = "Opal_Patronage_"
    suffix = ".txt"

    date = start

    end = datetime.date.today() - datetime.timedelta(days=1)

    while date <= end:
        url = f'{path}{date.strftime("%Y-%m")}/{prefix}{date.strftime("%Y%m%d")}{suffix}'
        urls.append(url)
        dates_strings.append(date.strftime("%Y-%m-%d"))
        date += datetime.timedelta(days=1)
    return urls, dates_strings


def request_files(force_new=False):
    with open(f'{dataLoc}rawData.txt') as f:
        first_line = f.readline()
        f.seek(0)
        old_text = f.read()
    if "Last-Updated" in first_line:
        last_update = first_line.split()[1]
        last_update = datetime.date.fromisoformat(last_update)
        if datetime.date.today() - last_update < datetime.timedelta(days=1):
            print("Transport data files up to date!")
            if not force_new:
                return True
    else:
        last_update = None

    if force_new:
        urls, dates = generate_end_urls()
    else:
        urls, dates = generate_end_urls(last_update)
    print(dates)
    with open(f'{dataLoc}rawData.txt', 'w') as f:
        f.write(f'Last-Updated: {datetime.date.today().isoformat()}\n')
        for i, url in enumerate(urls):
            response = requests.get(url, headers={'Referer': 'https://opendata.transport.nsw.gov.au/'})
            if response.status_code != 200:
                print(f'{response} failed for {url}')
                user_input = input("'abort' and revert or 'continue'").strip().lower()
                if user_input == "continue":
                    continue
                elif user_input == "abort":
                    print(f'Reverting to file made on {last_update}')
                    f.seek(0)
                    f.write(old_text)
                    return False
            s = str(response.content, 'utf-8')
            if i == 0:
                f.write(s[:-1])
            else:
                f.write(s[s.find('\n'):-1])
            # print('eye: ', i, len(urls))
            # time.sleep(1)
            print(
                f'\r{round((i + 1) / len(urls) * 100, 1)}% {dates[i]} {humanize.naturalsize(f.tell())} {i + 1}/{len(urls)} ',
                end='')


def process_data():
    with open(f'{dataLoc}rawData.txt') as f:
        first_line = f.readline()
        if "Last-Updated" not in first_line:
            print(f'Attempted reading empty file: {f}')
            return False

        f.readline()
        hour = 0
        dataSeriesByTransport = {}
        line_data = {'All - NSW': None}
        for i, line in enumerate(f):
            line = line.strip().split("|")
            if hour != int(line[3]):
                year, month, day = (int(x) for x in oldline[0].split('-'))
                dt = datetime.datetime(year=year, month=month, day=day, hour=hour)
                # print(dt)
                # print(*line[1:3], sep=' | ')
                # print(*line[4:6], sep=' | ')
                # print(line_data)
                series = pd.Series(line_data)
                mode = oldline[1]
                if not dataSeriesByTransport.get(mode):
                    dataSeriesByTransport[mode] = {}
                dataSeriesByTransport[mode][dt] = series
                line_data = {'All - NSW': None}
                hour = int(line[3])

                print('\r', i, end='')

            dayTapOnSum = 25 if '<' in line[4] else int(line[4])

            dayTapOffSum = 25 if '<' in line[5] else int(line[5])

            line_data[line[2]] = dayTapOnSum
            oldline = line

    data = {key: pd.DataFrame(data=val.values(), index=val.keys(), dtype=pd.Int64Dtype()) for key, val in
            dataSeriesByTransport.items()}
    return pd.concat(data, axis=1)


def process_tap_versus():
    with open(f'{dataLoc}rawData.txt') as f:
        first_line = f.readline()
        if "Last-Updated" not in first_line:
            print(f'Attempted reading empty file: {f}')
            return False
        f.readline()

        tapVersus = {}
        for i, line in enumerate(f):
            line = line.strip().split('|')
            if line[2] != "All - NSW":
                continue
            hour = int(line[3])
            year, month, day = (int(x) for x in line[0].split('-'))
            dt = datetime.datetime(year=year, month=month, day=day, hour=hour)

            if dt not in tapVersus:
                tapVersus[dt] = [0, 0]

            tapVersus[dt][0] += 25 if '<' in line[4] else int(line[4])
            tapVersus[dt][1] += 25 if '<' in line[5] else int(line[5])
    df = pd.DataFrame.from_dict(tapVersus, orient="index", columns=["tap-ons", "tap-offs"])

    df = aggregate(df, 7)

    return df


def write_data(data):
    with open(f'{dataLoc}transport.pkl', 'wb') as output:
        pickle.dump(data, output, -1)


def read_data():
    try:
        with open(f'{dataLoc}transport.pkl', 'rb') as inp:
            return pickle.load(inp)
    except FileNotFoundError:
        print('No preloaded file, creating new...')
        data = process_data()
        write_data(data)
        return data


def xs(df, modes=None, line=None):
    if modes and line:
        return df[modes].xs(line, axis=1, level=1)
    elif modes:
        return df[modes]
    else:
        return df.xs(line, axis=1, level=1)


def all_transport_sum(data):
    return data.sum(axis=1)


def aggregate(data, aggregatePeriod=7):
    def match_time_period(dt):
        return dt.timestamp() // datetime.timedelta(days=aggregatePeriod).total_seconds()

    grouped = data.groupby(by=match_time_period, group_keys=False)

    data = grouped.agg(np.mean)

    newIndex = [datetime.datetime.fromtimestamp(x * datetime.timedelta(days=aggregatePeriod).total_seconds()) for x in
                data.index]
    data.index = pd.DatetimeIndex(newIndex)
    return data


if __name__ == '__main__':
    # data = process_data()
    # profile.run("process_data()")
    # request_files(*generate_end_urls())
    # write_data(process_data())
    # data = read_data()

    # request_files(force_new=True)

    request_files(force_new=True)

    pass
