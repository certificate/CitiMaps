import csv
import time

class Station:
    def __init__(self, name, lat, lon, stationId):
        self.name = name
        self.latitude = lat
        self.longitue = lon
        self.stationId = stationId


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
                    stationList.append(Station(name, lat, lon, stationId))
                    skipList.append(stationId)


        # End calculations for time. My personal record on my home rig was 27 seconds (i7-6700K @ 4.4GHz)

        t1 = time.time()
        total = t1 - t0
        print("The whole operation took {} seconds.".format(round(total, 2)))

        print(len(stationList))

stationList = []

