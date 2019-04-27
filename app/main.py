from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, TapTool
from bokeh.plotting import figure, curdoc
from bokeh.tile_providers import get_provider, Vendors
import csvReader


# This is a Bokeh server application
# Run with >> bokeh serve --show app <<
# TODO: Get correcr

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

# START DATA SOURCES
map_source = ColumnDataSource(
    data=dict(lat=merc_x_list,
              lon=merc_y_list,
              station_name=station_names,
              station_unique=station_id)
)
segment_source = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

departures_source, hours, departures = csvReader.avg_hourly_departures_for_city()
# Save original departures data for whhen there is no selection
save_source = departures_source.data
# END DATA SOURCES


# Plot 1 (Map)
p_map = figure(x_range=merc_x_range, y_range=merc_y_range,
               x_axis_type="mercator", y_axis_type="mercator", plot_width=1440, plot_height=1080,
               title="Station locations in New York", toolbar_location="below")
p_map.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
circles = p_map.circle(x="lat", y="lon", size=10, fill_color="red", fill_alpha=0.8, source=map_source)
sr = p_map.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='red', alpha=0.6, line_width=3, source=segment_source)
p_map.add_tools(TapTool())

# Plot 2 (Departures)
p_dep = figure(x_range=hours, plot_height=525, plot_width=840, title="Hourly Departures - citywide",
               toolbar_location="right", tools="")
p_dep.vbar(x='hours', top='departures', width=0.9, source=departures_source)
p_dep.toolbar.logo = None

# Plot 3 (Averages - ride length etc.)
# TODO: Create a REAL plot. This is just for screen filler.
p_dep2 = figure(x_range=hours, plot_height=525, plot_width=840, title="Hourly Departures - citywide",
                toolbar_location="right", tools="")
v_bars = p_dep2.vbar(x='hours', top='departures', width=0.9, source=departures_source)
p_dep2.toolbar.logo = None

plot_pile = gridplot([[p_dep], [p_dep2]])
site_layout = gridplot([[p_map, plot_pile]])

curdoc().add_root(site_layout)
curdoc().title = "CitiBike Data"
curdoc().theme = 'dark_minimal'


# Callback function that is activated when an item is >>selected<<
def update(attr, old, new):
    global segment_source
    selected = map_source.selected.indices
    selected_items = len(selected)

    print("Map data source OnSelected:" + "\n")

    for item in selected:
        print("Station name for ID " + str(item) + " is: " + str(station_names[item]))

    if selected_items != 2:
        clear_screen()

        if selected_items > 2:
            map_source.selected.indices = []

    if selected_items == 2:
        map_segment(selected)

    if selected_items == 1:
        set_departures(selected[0])

    if selected_items == 0:
        set_departures("city")


def clear_screen():
    sr.data_source.data = {'x0': [], 'y0': [], 'x1': [], 'y1': []}


def map_segment(selected):
    global sr
    segData = {'x0': [], 'y0': [], 'x1': [], 'y1': []}

    segData['x0'].append(map_source.data['lat'][selected[0]])
    segData['y0'].append(map_source.data['lon'][selected[0]])
    segData['x1'].append(map_source.data['lat'][selected[1]])
    segData['y1'].append(map_source.data['lon'][selected[1]])

    sr.data_source.data = segData


def set_departures(id_station):
    if id_station == "city":
        v_bars.data_source.data = save_source

    else:
        v_bars.data_source.data = csvReader.calc_departures_per_hour(id_station)


circles.data_source.selected.on_change('indices', update)
