from bokeh.models import ColumnDataSource, CustomJS, TapTool
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import CARTODBPOSITRON_RETINA

import bokeh
import csvReader


def stations_to_lists(stations):
    merc_x = []
    merc_y = []
    names = []
    station_id = []

    for station in stations:
        merc_x.append(station.merc_x)
        merc_y.append(station.merc_y)
        names.append(station.name)
        station_id.append(station.stationId)
        print("Did one!")

    return merc_x, merc_y, names, station_id


def get_data():
    csvReader.import_data()


def main():
    print("Running main function")
    output_file("plot.html")

    get_data()

    stations = csvReader.stationList

    merc_x_list, merc_y_list, names, station_id = stations_to_lists(stations)

    # define x and y ranges
    merc_x_range = [a(merc_x_list) for a in [min, max]]
    merc_y_range = [a(merc_y_list) for a in [min, max]]

    source = ColumnDataSource(
        data=dict(lat=merc_x_list,
                  lon=merc_y_list,
                  station_name=names,
                  station_unique=station_id)
    )


    TOOLTIPS = [
        ("stationID", "@station_unique"),
        ("station", "@station_name"),
        ("X-coordinate", "@lat"),
        ("Y-coordinate", "@lon")
    ]

    # range bounds supplied in web mercator coordinates
    p = figure(x_range=merc_x_range, y_range=merc_y_range,
               x_axis_type="mercator", y_axis_type="mercator", plot_width=1920, plot_height=1080,
               tooltips=TOOLTIPS, title="Station locations in New York")
    p.circle(x="lat", y="lon", size=10, fill_color="red", fill_alpha=0.8, source=source)
    p.add_tile(CARTODBPOSITRON_RETINA)


    # Code for the callback
    code = """
    
    
    // Set column name to select similar glyphs
    var column = 'station_unique';

    // Get data from ColumnDataSource
    var data = source.data;

    // Get indices array of all selected items
    var selected = source.selected.indices;

    for (item in selected){
        console.log("Station name for ID "+ selected[item] + " is: " + station_name[item])
    }
    
    
    
    """

    callback = CustomJS(args={'source': source, 'station_name':names, 'station_id':station_id}, code=code)
    p.add_tools(TapTool(callback=callback))

    show(p)


if __name__ == '__main__':
    main()
