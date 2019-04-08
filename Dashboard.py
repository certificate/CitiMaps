from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import CARTODBPOSITRON_RETINA

import csvReader


def stations_to_lists(stations):
    merc_x = []
    merc_y = []

    for station in stations:
        merc_x.append(station.merc_x)
        merc_y.append(station.merc_y)
        print("Did one!")

    return merc_x, merc_y


def get_data():
    csvReader.import_data()


def main():
    print("Running main function")
    output_file("plot.html")

    get_data()

    stations = csvReader.stationList

    merc_x_list, merc_y_list = stations_to_lists(stations)

    # define x and y ranges
    merc_x_range = [a(merc_x_list) for a in [min, max]]
    merc_y_range = [a(merc_y_list) for a in [min, max]]

    source = ColumnDataSource(
        data=dict(lat=merc_x_list,
                  lon=merc_y_list)
    )

    TOOLTIPS = [
        ("index", "$index"),
        ("(X-coordinate)", "(@lat)"),
        ("(Y-coordinate)", "(@lon)")
    ]

    # range bounds supplied in web mercator coordinates
    p = figure(x_range=merc_x_range, y_range=merc_y_range,
               x_axis_type="mercator", y_axis_type="mercator", plot_width=1280, plot_height=720,
               tooltips=TOOLTIPS, title="Station locations in New York")
    p.circle(x="lat", y="lon", size=10, fill_color="red", fill_alpha=0.8, source=source)
    p.add_tile(CARTODBPOSITRON_RETINA)


    show(p)


if __name__ == '__main__':
    main()


