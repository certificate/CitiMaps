import csv
import time
import csvReader
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, TapTool
from bokeh.plotting import figure, curdoc
from bokeh.tile_providers import get_provider, Vendors


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


stations = csvReader.import_data()

merc_x_list, merc_y_list, station_names, station_id = stations_to_lists(stations)

# define x and y ranges
merc_x_range = [a(merc_x_list) for a in [min, max]]
merc_y_range = [a(merc_y_list) for a in [min, max]]

source = ColumnDataSource(
    data=dict(lat=merc_x_list,
              lon=merc_y_list,
              station_name=station_names,
              station_unique=station_id)
)
segment_source = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

# create a plot and style its properties
p = figure(x_range=merc_x_range, y_range=merc_y_range,
           x_axis_type="mercator", y_axis_type="mercator", plot_width=1920, plot_height=1080,
           title="Station locations in New York")
p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
circles = p.circle(x="lat", y="lon", size=10, fill_color="red", fill_alpha=0.8, source=source)
sr = p.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='red', alpha=0.6, line_width=3, source=segment_source)
p.add_tools(TapTool())


# put the plot in a layout and add to the document
curdoc().add_root(column(p))


# Callback function that is activated when an item is >>selected<<
def update(attr, old, new):
    global segment_source
    selected = source.selected.indices

    print("\n" + "Data Source changed! Updating:" + "\n")

    for item in selected:
        print("Station name for ID " + str(item) + " is: " + str(station_names[item]))

    if len(selected) != 2:
        remove_segment()

        if len(selected) > 2:
            source.selected.indices = []

    if len(selected) == 2:
        map_segment(selected)

    print("Done.")

def remove_segment():
    sr.data_source.data = {'x0': [], 'y0': [], 'x1': [], 'y1': []}


def map_segment(selected):
    global sr
    segData = {'x0': [], 'y0': [], 'x1': [], 'y1': []}

    segData['x0'].append(source.data['lat'][selected[0]])
    segData['y0'].append(source.data['lon'][selected[0]])
    segData['x1'].append(source.data['lat'][selected[1]])
    segData['y1'].append(source.data['lon'][selected[1]])

    sr.data_source.data = segData


circles.data_source.selected.on_change('indices', update)
