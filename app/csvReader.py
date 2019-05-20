import csv
from datetime import datetime
import time
import math
from collections import Counter

from bokeh.models import ColumnDataSource

filename = "citi3.csv"


class Station:
    def __init__(self, name, lat, lon, stationId, merc_x, merc_y):
        self.name = name
        self.latitude = lat
        self.longitue = lon
        self.stationId = stationId
        self.merc_x = merc_x
        self.merc_y = merc_y


# converts (lat,lon) into mercator_x and mercator_y coordinates
def merc(lat, lon):
    r_major = 6378137.000
    x = r_major * math.radians(lon)
    scale = x / lon
    y = 180.0 / math.pi * math.log(math.tan(math.pi / 4.0 +
                                            lat * (math.pi / 180.0) / 2.0)) * scale
    return x, y


def import_data():
    # Array for all the stations.
    stationList = []

    # Time the task just to see how efficient it is.
    t0 = time.time()

    # Let's open the behemoth of a file! (Close to 5 million lines of sweet, sweet data!) Remember to check if your
    # file has been named differently. Filename underneath was the one I got from unpacking the zip file.
    with open(filename, 'r', encoding='latin-1') as data:
        reader = csv.reader(data, delimiter=",")
        print("Working...")

        # Skipping the first row. Doesn't containt anything but the explanations.
        for _ in range(0, 1):
            next(data)

        # Go through the entire file line by line, doing subtasks whenever encountering a
        # certain type of a vehicle.

        skipList = []
        for line in reader:

            # type of the vehicle
            lat = line[5]
            lon = line[6]
            stationId = line[3]
            name = line[4]

            if (lat, lon, stationId, name) is not None:

                if stationId not in skipList:
                    merc_x, merc_y = merc(float(lat), float(lon))

                    stationList.append(Station(name, lat, lon, stationId, merc_x, merc_y))
                    skipList.append(stationId)

        t1 = time.time()
        total = t1 - t0
        print("The whole operation took {} seconds.".format(round(total, 2)))

        print(len(stationList))
        return stationList


def calc_departures_per_hour(station_id):
    # Time the task just to see how efficient it is.
    t0 = time.time()
    departures = []
    hourly_dep = []

    with open(filename, 'r', encoding='latin-1') as data:
        reader = csv.reader(data, delimiter=",")
        # Skip the first row. Doesn't contain anything but the data formats.
        for _ in range(0, 1):
            next(data)
        for line in reader:
            stationIdCSV = line[0]

            if int(stationIdCSV) == int(station_id):

                if filename == "citi3.csv":
                    # 2/1/2015 0:04
                    master_split = line[1].split(' ')
                    time_split = master_split[1].split(':')
                    seconds = time_split[0]

                else:
                    # Line[1] = Departure Time. Format: '2019-01-01 00:01:47.4010'
                    master_split = line[1].split(' ')
                    date_split = master_split[0].split('-')
                    time_split = master_split[1].split(':')
                    seconds_split = time_split[2].split('.')
                    seconds = seconds_split[0]

                    departure = datetime(year=int(date_split[0]),
                                         month=int(date_split[1]),
                                         day=int(date_split[2]),
                                         hour=int(time_split[0]),
                                         minute=int(time_split[1]),
                                         second=int(seconds))

                    departures.append(departure)

                hourly_dep.append(time_split[0])

    hours = []
    values = []
    for i in range(24):
        hours.append(str(i))
        values.append(hourly_dep.count(str(i)))

    mydata = dict(hours=hours,
                  departures=values)

    t1 = time.time()
    total = t1 - t0
    # print("The departure calculation took {} seconds.".format(round(total, 2)))
    return mydata


def avg_hourly_departures_for_city():
    # Time the task just to see how efficient it is.
    t0 = time.time()
    departures = []
    hourly_dep = []

    with open(filename, 'r', encoding='latin-1') as data:
        reader = csv.reader(data, delimiter=",")
        # Skip the first row. Doesn't contain anything but the data formats.
        for _ in range(0, 1):
            next(data)
        for line in reader:

            # Different .csv's have different formats...
            if (filename == "citi3.csv"):
                # 2/1/2015 0:04
                master_split = line[1].split(' ')
                time_split = master_split[1].split(':')
                hour = time_split[0]

            else:
                # Line[1] = Departure Time. Format: '2019-01-01 00:01:47.4010'
                master_split = line[1].split(' ')
                date_split = master_split[0].split('-')
                time_split = master_split[1].split(':')
                seconds_split = time_split[2].split('.')
                hour = time_split[0]
                seconds = seconds_split[0]

                departure = datetime(year=int(date_split[0]),
                                     month=int(date_split[1]),
                                     day=int(date_split[2]),
                                     hour=int(time_split[0]),
                                     minute=int(time_split[1]),
                                     second=int(seconds))

                departures.append(departure)

            hourly_dep.append(hour)

    counted = dict(Counter(hourly_dep))
    data_source = ColumnDataSource(
        data=dict(hours=list(counted.keys()),
                  departures=list(counted.values()))
    )

    t1 = time.time()
    total = t1 - t0
    print("The citywide departure calculation took {} seconds.".format(round(total, 2)))
    return data_source, list(counted.keys()), list(counted.values())


def calc_men_and_women(stationId):
    # Time the task just to see how efficient it is.
    t0 = time.time()
    males = 0
    females = 0
    uknown = 0

    with open(filename, 'r', encoding='latin-1') as data:
        reader = csv.reader(data, delimiter=",")
        # Skip the first row. Doesn't contain anything but the data formats.
        for _ in range(0, 1):
            next(data)
        for line in reader:
            stationIdCSV = line[0]

            if int(stationIdCSV) == int(stationId):
                gender = int(line[14])

                if gender == 1:
                    males = males + 1
                elif gender == 2:
                    females = females + 1
                elif gender == 0:
                    uknown = uknown + 1

    t1 = time.time()
    total = t1 - t0
    # print("The departure calculation took {} seconds.".format(round(total, 2)))
    return males, females, uknown


def get_departures_for_station(station_id):
    with open('departures.csv', 'r', encoding='latin-1') as data:
        reader = csv.reader(data, delimiter=";")
        # Skip the first two rows. Doesn't contain anything but the data formats.
        for _ in range(0, 2):
            next(data)
        for line in reader:
            stationIdCSV = line[0]

            if int(stationIdCSV) == int(station_id):
                return line[1], line[2]


def get_sexes(station_id):
    men = 0
    women = 0
    others = 0
    with open('departures.csv', 'r', encoding='latin-1') as data:
        reader = csv.reader(data, delimiter=";")
        # Skip the first two rows. Doesn't contain anything but the data formats.

        for _ in range(0, 2):
            next(data)
        for line in reader:
            stationIdCSV = line[0]

            if int(stationIdCSV) == int(station_id):
                return line[3], line[4], line[5]

            elif station_id == -1:
                men = men + int(line[3])
                women = women + int(line[4])
                others = others + int(line[5])

    return str(men), str(women), str(others)

