import threading
import time
import ast
from math import pi

import pandas as pd
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, TapTool, Title
from bokeh.plotting import figure, curdoc
from bokeh.tile_providers import get_provider, Vendors
from bokeh.transform import dodge, linear_cmap, cumsum
from bokeh.palettes import plasma
from bokeh.palettes import Plasma, Category20c

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

# Map
map_source = ColumnDataSource(
    data=dict(lat=merc_x_list,
              lon=merc_y_list,
              station_name=station_names,
              station_unique=station_id)
)

# Segment between two circles
segment_source = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

# Departures [also save original departures data for whhen there is no selection]
departures_source, hours, departures = csvReader.avg_hourly_departures_for_city()
save_source = departures_source.data

# Second departures
second_departures = ColumnDataSource(
    data=dict(hours=[],
              departures=[])
)

# Sexes
men, women, others = csvReader.get_sexes(-1)
sexes = [men, women, others]
genders = ["Men", "Women", "Others"]
sexes = list(map(int, sexes))
x = dict(zip(genders, sexes))
data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'sex'})
data['angle'] = data['value'] / data['value'].sum() * 2 * pi
data['color'] = ['#E5827E', '#F6A16C', '#F7E44E']

# END DATA SOURCES
# Color mappers
circle_mapper = linear_cmap(field_name='lat', palette=plasma(256), low=min(merc_x_list), high=max(merc_x_list))
segment_mapper = linear_cmap(field_name='x0', palette=plasma(256), low=min(merc_x_list), high=max(merc_x_list))

# Plot 1 (Map)
p_map = figure(x_range=merc_x_range, y_range=merc_y_range,
               x_axis_type="mercator", y_axis_type="mercator", plot_width=1440, plot_height=1080,
               title="Station locations in New York", toolbar_location="below", tooltips=[
        ("Name", "@station_name")])
p_map.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
circles = p_map.circle(x="lat", y="lon", size=10, fill_alpha=0.8, source=map_source, line_color=circle_mapper,
                       color=circle_mapper)
sr = p_map.segment(x0='x0', y0='y0', x1='x1', y1='y1', line_color=segment_mapper, color=segment_mapper, alpha=0.6,
                   line_width=3, source=segment_source)
p_map.add_tools(TapTool())

# Plot 2 (Departures)
p_dep = figure(x_range=hours, plot_height=525, plot_width=840, title="Hourly Departures - citywide",
               toolbar_location="right", tools="", tooltips=[("Departures", "@departures")])
v_bars = p_dep.vbar(x=dodge('hours', 0.0, range=p_dep.x_range),
                    top='departures', width=0.4, source=departures_source, color="#E5827E")
v_bars_second = p_dep.vbar(x=dodge('hours', 0.4, range=p_dep.x_range),
                           top='departures', width=0.4, source=second_departures, color="#F7E44E")
p_dep.x_range.range_padding = 0.2

p_dep.toolbar.logo = None

# Plot 3 (Averages - ride length etc.)
# TODO: Create a REAL plot. This is just for screen filler.
p_sex = figure(plot_height=525, plot_width=840, title="Gender distribution", toolbar_location=None,
               tools="hover", tooltips="@sex: @value", x_range=(-0.75, 0.75))
p_wedge = p_sex.wedge(x=0, y=1, radius=0.4,
                      start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                      line_color="white", fill_color='color', legend='sex', source=data)
p_sex.toolbar.logo = None

plot_pile = gridplot([[p_dep], [p_sex]])
site_layout = gridplot([[p_map, plot_pile]])

curdoc().add_root(site_layout)
curdoc().title = "CitiBike Data"
curdoc().theme = 'dark_minimal'


# Callback function that is activated when an item is >>selected<<
def set_sexes(station_id):
    men, women, others = csvReader.get_sexes(station_id)
    sexes = [men, women, others]
    genders = ["Men", "Women", "Others"]
    sexes = list(map(int, sexes))
    x = dict(zip(genders, sexes))
    newData = pd.Series(x).reset_index(name='value').rename(columns={'index': 'sex'})
    newData['angle'] = newData['value'] / newData['value'].sum() * 2 * pi
    newData['color'] = ['#E5827E', '#F6A16C', '#F7E44E']

    new_source = ColumnDataSource(
        data=newData
    )
    p_wedge.data_source.data = new_source.data


def set_sexes_second(first_station_id, second_station_id):
    men1, women1, others1 = csvReader.get_sexes(first_station_id)
    men2, women2, others2 = csvReader.get_sexes(second_station_id)
    men = int(men1) + int(men2)
    women = int(women1) + int(women2)
    others = int(others1) + int(others2)
    sexes = [men, women, others]
    genders = ["Men", "Women", "Others"]
    sexes = list(map(int, sexes))
    x = dict(zip(genders, sexes))
    newData = pd.Series(x).reset_index(name='value').rename(columns={'index': 'sex'})
    newData['angle'] = newData['value'] / newData['value'].sum() * 2 * pi
    newData['color'] = ['#E5827E', '#F6A16C', '#F7E44E']

    new_source = ColumnDataSource(
        data=newData
    )
    p_wedge.data_source.data = new_source.data


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
        set_second_station_departures(station_id[selected[0]])
        set_sexes_second(station_id[selected[0]], station_id[selected[1]])

    if selected_items == 1:
        set_departures(station_id[selected[0]])
        set_sexes(station_id[selected[0]])
        clear_second_bars()

    if selected_items == 0:
        set_departures("city")
        set_sexes(-1)
        clear_second_bars()


def clear_screen():
    sr.data_source.data = {'x0': [], 'y0': [], 'x1': [], 'y1': []}


def clear_second_bars():
    v_bars_second.data_source.data = dict(hours=[],
                                          departures=[],
                                          departures_2=[])


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
        p_dep.title.text = "Hourly Departures - citywide"

    else:
        new_hours, new_deps = csvReader.get_departures_for_station(id_station)
        new_hours = ast.literal_eval(new_hours)
        new_deps = ast.literal_eval(new_deps)
        v_bars.data_source.data = dict(hours=new_hours,
                                       departures=new_deps)
        p_dep.title.text = "Hourly Departures - " + get_station_name(id_station)


def set_second_station_departures(second_station_id):
    current_hours = v_bars.data_source.data['hours']
    new_hours, new_deps = csvReader.get_departures_for_station(second_station_id)
    new_hours = ast.literal_eval(new_hours)
    new_deps = ast.literal_eval(new_deps)
    v_bars_second.data_source.data = dict(hours=new_hours,
                                          departures=new_deps)
    p_dep.title.text = p_dep.title.text + " and " + get_station_name(second_station_id)


def get_station_name(stationId):
    for station in stations:
        if station.stationId == stationId:
            return station.name


circles.data_source.selected.on_change('indices', update)
