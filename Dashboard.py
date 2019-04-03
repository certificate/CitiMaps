from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import CARTODBPOSITRON_RETINA

import csvReader


def stations_to_lists(stations):
    lat = []
    lon = []

    for station in stations:
        lat.append(station.latitude)
        lon.append(station.longitue)
        print("Did one!")

    return lat, lon


def get_data():
    csvReader.import_data()


def main():
    print("Running main function")
    output_file("tile.html")

    get_data()

    stations = csvReader.stationList

    # range bounds supplied in web mercator coordinates
    p = figure(x_range=(-2000000, 6000000), y_range=(-1000000, 7000000),
               x_axis_type="mercator", y_axis_type="mercator")

    latlist, lonlist = stations_to_lists(stations)

    source = ColumnDataSource(
        data=dict(lat=latlist,
                  lon=lonlist)
    )

    p.circle(x="lon", y="lat", size=15, fill_color="blue", fill_alpha=0.8, source=source)

    p.add_tile(CARTODBPOSITRON_RETINA)

    show(p)


if __name__ == '__main__':
    main()


