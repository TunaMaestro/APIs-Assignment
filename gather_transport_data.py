import pandas
import requests
import datetime
import humanize
import pandas as pd
import numpy as np
import profile
import _pickle as pickle

def generate_end_urls():
    urls = []
    dates_strings = []
    path = "https://tfnsw-prod-opendata-tpa.s3-ap-southeast-2.amazonaws.com/Opal_Patronage/"
    prefix = "Opal_Patronage_"
    suffix = ".txt"
    date = datetime.date(2020, 1, 1)

    end = datetime.date.today()

    while date <= end:
        url = path + f'{date.strftime("%Y-%m")}/{prefix}{date.strftime("%Y%m%d")}{suffix}'
        urls.append(url)
        dates_strings.append(date.strftime("%Y-%m-%d"))
        date += datetime.timedelta(days=1)
    return urls, dates_strings


def request_files(urls, dates, force_new=False):
    with open('rawData.txt') as f:
        first_line = f.readline()
        f.seek(0)
        old_text = f.read()
    if "Last-Updated" in first_line:
        last_update = first_line.split()[1]
        if datetime.date.today() - datetime.date.fromisoformat(last_update) < datetime.timedelta(days=1):
            print("File up to date!")
            if not force_new:
                return True

    with open('rawData.txt', 'w') as f:
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
    all = pd.DataFrame()
    with open('rawData copy 3.txt') as f:
        first_line = f.readline()
        if "Last-Updated" not in first_line:
            print(f'Attempted reading empty file: {f}')
            return False
        # data = {}
        # for header in f.readline().strip().split('|'):
        #     data[header] = []
        # print(data)
        f.readline()
        hour = 0
        dataSeriesByTransport = {}
        line_data = {'All - NSW': None}
        for i, line in enumerate(f):
            line = line.strip().split("|")
            if hour != int(line[3]):
                year, month, day = (int(x) for x in oldline[0].split('-'))
                # print(year,month,day,hour)
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

            dayTapSum = sum(25 if '<' in x else int(x) for x in line[4:6])
            line_data[line[2]] = dayTapSum
            oldline = line

    bus = dataSeriesByTransport['Bus']
    data = {key: pd.DataFrame(data=val.values(), index=val.keys(), dtype=pd.Int64Dtype()) for key, val in dataSeriesByTransport.items()}
    return pd.concat(data, axis=1)

def write_data(data):
    with open('transport.pkl', 'wb') as output:
        pickle.dump(data, output, -1)

def read_data():
    with open('transport.pkl', 'rb') as inp:
        return pickle.load(inp)

def all_transport_sum(data):

    sums = data.xs('All - NSW', axis=1, level=1).sum(axis=1)

    aggregatePeriod = 7
    def match_time_period(dt):
        return dt.timestamp() // datetime.timedelta(days=aggregatePeriod).total_seconds()

    grouped = sums.groupby(by=match_time_period, group_keys=False)

    sums = grouped.agg(np.mean)

    newIndex = [datetime.datetime.fromtimestamp(x * datetime.timedelta(days=aggregatePeriod).total_seconds()) for x in sums.index]
    sums.index = pandas.DatetimeIndex(newIndex)
    return sums

if __name__ == '__main__':
    # urls, dates = generate_end_urls()
    # request_files(urls, dates)
    # data = process_data()
    # profile.run("process_data()")
    write_data(process_data())

    pass