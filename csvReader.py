import csv
from datetime import datetime
import time
import math


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
    # Array for all the different variables which we will be using later.

    # Time the task just to see how efficient it is.
    t0 = time.time()

    # Let's open the behemoth of a file! (Close to 5 million lines of sweet, sweet data!) Remember to check if your
    # file has been named differently. Filename underneath was the one I got from unpacking the zip file.
    with open("citibike.csv", 'r', encoding='latin-1') as data:
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


def calc_departures_per_hour(station_id):
    print("Calculating departures per hour for " + station_id)
    # Time the task just to see how efficient it is.
    t0 = time.time()
    departures = []

    with open("citibike.csv", 'r', encoding='latin-1') as data:
        reader = csv.reader(data, delimiter=",")
        # Skip the first row. Doesn't contain anything but the data formats.
        for _ in range(0, 1):
            next(data)
        for line in reader:
            stationIdCSV = line[3]

            if (stationIdCSV == station_id):
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

    t1 = time.time()
    total = t1 - t0
    print("The departure operation took {} seconds.".format(round(total, 2)))


stationList = []
