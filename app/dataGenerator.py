import csv
import time
import csvReader


def write_headers():
    with open('departures.csv', mode='w', encoding='latin-1') as data_file:
        writer = csv.writer(data_file, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE, escapechar='\\')
        writer.writerow(["station_id", "hours", "departures"])


def write_to_csv(id, hours, deps):
    with open('departures.csv', mode='a', newline='', encoding='latin-1') as data_file:
        writer = csv.writer(data_file, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE, escapechar='\\')
        writer.writerow([id, hours, deps])


filename = "citi3.csv"
# Array for all the stations.
stationList = []

write_headers()

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
                deps = csvReader.calc_departures_per_hour(stationId)
                write_to_csv(stationId, deps['hours'], deps['departures'])

                skipList.append(stationId)

    t1 = time.time()
    total = t1 - t0
    print("The whole operation took {} seconds.".format(round(total, 2)))

    print(len(stationList))
