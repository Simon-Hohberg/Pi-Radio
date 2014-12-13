function StationList(data) {
    
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
            station.setIndex(i - 1);
            self.stations[i - 1] = station;
        }
        self.stations.pop();
    };
    
    this.getURIList = function() {
        var list = [];
        for (var i = 0; i < self.stations.length; i++) {
            list.push(self.stations[i].getUri());
        }
        return list;
    };

    this.reload = function(data) {
        for ( var i = 0; i < self.stations.length; i++ ) {
            this.stations[i].remove()
        }
        this.stations = [];
        for (var i = 0; i < data.length; i++) {
            this.addStation(data[i][0], data[i][1]);
        }
    };

    this.toArray = function() {
        var arr = new Array(this.stations.length);
        for (var i = 0; i < this.stations.length; i++) {
            var station = this.stations[i];
            arr[i] = new Array(2);
            arr[i][0] = station.getName();
            arr[i][1] = station.getUri();
        }
        return arr;
    }
    
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
                    station.setIndex(i - 1)
                }
            } else {
                for (var i = startPos - 1; i >= index; i--) {
                    var station = self.stations[i];
                    self.stations[i + 1] = station;
                    station.setIndex(i + 1);
                }
            }
            movedStation.setIndex(index);
            self.stations[index] = movedStation;
        },
        
        update: function(event, ui) {
            $( "#sortable li" ).removeClass( "highlights" );
        }
    });
    
    this.stations = [];
    this.max = 10;
    this.reload(data);
    
    $( "#station-list" ).disableSelection();
}
