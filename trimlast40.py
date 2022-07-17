import json
with open('sydneypast40years.json') as f:
    j = json.load(f)
    for i, val in enumerate(j):
        if int(val['dt']) >= 1577836800: # dt of start of 2020
            break
    out = j[i:]
with open('staticWeatherFrom2020.json', 'w') as f:
    json.dump(out, f)