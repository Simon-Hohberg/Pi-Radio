function StationList(data, stationMax) {
    
    var self = this;
    
    this.addStation = function (name, uri) {
        if (this.stations.length < this.max) {
            var station = new Station(this.stations.length, name, uri);
            this.stations.push(station);
            station.setOnRemoveListener(self.removeStation);
        } else {
            // TODO
        }
    };
    
    this.removeStation = function (index) {
        var removedStation = self.stations[index];
        removedStation.remove();
        for ( var i = index + 1; i < self.stations.length; i++ ) {
            var station = self.stations[i];
            station.setLabel( i + " - " );
            self.stations[i - 1] = station;
            station.index = i - 1;
        }
        self.stations.pop();
    };
    
    this.getURIList = function() {
        var list = [];
        for (var i = 0; i < self.stations.length; i++) {
            list.push(self.stations[i].getURI());
        }
        return list;
    };
    
    $( "#station-list" ).sortable({
        start: function(event, ui) {
            var start_pos = ui.item.index();
            ui.item.data( "start_pos", start_pos );
        },
        
        stop: function(event, ui) {
            var startPos = ui.item.data( "start_pos" ) - 1;
            var index = ui.item.index() - 1;
            
            var movedStation = self.stations[startPos];
            
            if (startPos < index) {
                for (var i = startPos + 1; i <= index; i++) {
                    var station = self.stations[i];
                    self.stations[i - 1] = station;
                    station.index = i - 1;
                    $("label", station.widget).text( i + " - " );
                }
            } else {
                for (var i = startPos - 1; i >= index; i--) {
                    var station = self.stations[i];
                    self.stations[i + 1] = station;
                    station.index = i + 1;
                    $("label", station.widget).text( (i + 2) + " - " );
                }
            }
            
            self.stations[index] = movedStation;
            $( "label", movedStation.widget ).text( (index + 1) + " - " );
            
            sendStationList(self.getURIList(), function() {
               // TODO error handling 
            });
        },
        
        update: function(event, ui) {
            $( "#sortable li" ).removeClass( "highlights" );
        }
    });
    
    this.stations = [];
    this.max = stationMax;
    for (var i = 0; i < data.length; i++) {
        this.addStation(data[i][0], data[i][1]);
    }
    
    $( "#station-list" ).disableSelection();
}
