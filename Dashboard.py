from bokeh.models import ColumnDataSource, CustomJS, TapTool
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors

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

    print("All stations converted to lists")
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
    segment_source = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

    # Here for test purposes
    csvReader.calc_departures_per_hour(station_id[0])


    TOOLTIPS = [
        ("stationID", "@station_unique"),
        ("station", "@station_name"),
        ("X-coordinate", "@lat"),
        ("Y-coordinate", "@lon")
    ]

    TOOLS = "pan,wheel_zoom,box_zoom,box_select,lasso_select,reset,hover,save,help"

    # range bounds supplied in web mercator coordinates
    p = figure(x_range=merc_x_range, y_range=merc_y_range,
               x_axis_type="mercator", y_axis_type="mercator", plot_width=1920, plot_height=1080,
               tooltips=TOOLTIPS, title="Station locations in New York")
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
    p.circle(x="lat", y="lon", size=10, fill_color="red", fill_alpha=0.8, source=source)
    sr = p.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='red', alpha=0.6, line_width=3, source=segment_source)


    # Code for the callback
    code = """
    
    
    function removeSegment() {
        var emptyData = {'x0': [], 'y0': [], 'x1': [], 'y1': []};
        segment.data = emptyData;
    }

    // Set column name to select similar glyphs
    var column = 'station_unique';

    // Get data from ColumnDataSource
    var data = source.data;

    // Get indices array of all selected items
    var selected = source.selected.indices;
    console.log(selected.length); // 3
    
    // Remove segment if only 1 dot selected
    if (selected.length == 1){
        removeSegment()
    }
    
    if (selected.length > 2){
        console.log("Too many! Closing selections.");
        source.selected.indices = [];
        removeSegment()
    }

    for (item in selected){
        console.log("Station name for ID "+ selected[item] + " is: " + station_name[item])
        console.log(cb_data)
    }

    if (selected.length == 2){

        var selID = selected[0]
        var segData = {'x0': [], 'y0': [], 'x1': [], 'y1': []};

        segData['x0'].push(data.lat[selected[0]]);
        segData['y0'].push(data.lon[selected[0]]);
        segData['x1'].push(data.lat[selected[1]]);
        segData['y1'].push(data.lon[selected[1]]);

        segment.data = segData;

    }
    
    
    """

    callback = CustomJS(args={'source': source, 'station_name':names, 'station_id':station_id, 'segment': sr.data_source}, code=code)
    p.add_tools(TapTool(callback=callback))

    show(p)


if __name__ == '__main__':
    main()
