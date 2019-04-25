def item_click_event():
    # Code for the callback
    return """
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
        console.log(selected.length);

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