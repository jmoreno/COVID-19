#!/usr/bin/env python

# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/

# Written by Francois Fleuret <francois@fleuret.org>

import os, time
import numpy, csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import urllib.request

######################################################################

def gentle_download(url, delay = 86400):
    filename = url[url.rfind('/') + 1:]
    if not os.path.isfile(filename) or os.path.getmtime(filename) < time.time() - delay:
        print(f'Retrieving {url}')
        urllib.request.urlretrieve(url, filename)
    return filename

######################################################################

nbcases_filename = gentle_download(
    'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
)

######################################################################

with open(nbcases_filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    times = []
    nb_cases = {}
    time_col = 5
    for row_nb, row in enumerate(reader):
        for col_nb, field in enumerate(row):
            if row_nb == 0 and col_nb >= time_col:
                times.append(time.mktime(time.strptime(field, '%m/%d/%y')))
            if row_nb >= 1:
                if col_nb == 1:
                    country = field
                    if not country in nb_cases:
                        nb_cases[country] = numpy.zeros(len(times))
                elif col_nb >= time_col:
                    nb_cases[country][col_nb - time_col] += int(field)

countries = list(nb_cases.keys())
countries.sort()

nb_cases['World'] = sum(nb_cases.values())

######################################################################

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax.yaxis.grid(color='gray', linestyle='-', linewidth=0.25)
ax.set_title('Nb. of COVID-19 cases')
ax.set_xlabel('Date', labelpad = 10)

# Comment out next to line to make the graph linear.
ax.set_yscale('log')

myFmt = mdates.DateFormatter('%b %d')

ax.xaxis.set_major_formatter(myFmt)
dates = mdates.epoch2num(times)

# Source: https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population
populations = {
    "China":     1401826880,
    "US":         329476630,
    "Japan":      126010000,
    "France":      67069000,
    "UK":          66435600,
    "Italy":       60243406,
    "Korea, South": 51780579,
}

# This line divides number of cases by population. Comment out if you want absolute numbers.
nb_cases = {key: numpy.array([(v / populations[key] * 100) for v in value]) for key, value in nb_cases.items() if key in populations}

for key, color, label in [
#        ('World', 'black', 'World'),
        ('France', 'blue', 'France'),
        ('US', 'red', 'USA'),
        ('Korea, South', 'green', 'South Korea'),
        ('Italy', 'purple', 'Italy'),
        ('China', 'orange', 'China')
]:
    ax.plot(dates, nb_cases[key],
            color = color, label = label, linewidth = 2)

ax.legend(frameon = False)

plt.show()

fig.savefig('covid19_nb_cases.png')

######################################################################
