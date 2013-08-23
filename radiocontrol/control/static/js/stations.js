$(function() {
    
    
});


function StationList(urls, stationMax) {
    
    var self = this;
    this.stations = [];
    this.max = stationMax;
    for (var i = 0; i < urls.length; i++) {
        this.stations.push( new Station( i, urls[i] ) );
    }
    
    this.addStation = function (url) {
        if (this.stations.length < this.max) {
            this.stations.push(new Station(this.stations.length, url));
        } else {
            // TODO
        }
    };
    
    this.removeStation = function (index) {
        var removedStation = this.stations[index];
        removedStation.remove();
        for ( var i = index + 1; i < this.stations.length; i++ ) {
            var station = this.stations[i];
            station.setLabel( i + " - " );
            this.stations[i - 1] = station;
        }
        this.stations.pop();
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
                    $("label", station.widget).text( i + " - " );
                }
            } else {
                for (var i = startPos - 1; i >= index; i--) {
                    var station = self.stations[i];
                    self.stations[i + 1] = station;
                    $("label", station.widget).text( (i + 2) + " - " );
                }
            }
            
            self.stations[index] = movedStation;
            $( "label", movedStation.widget ).text( (index + 1) + " - " );
        },
        
        update: function(event, ui) {
            $( "#sortable li" ).removeClass( "highlights" );
        }
    });
    $( "#station-list" ).disableSelection();
}

function Station(index, url) {
    
    this.setLabel = function (text) {
        $( "label", this.widget ).text( text );
    }
    
    this.remove = function () {
        this.widget.remove();
    }
    
    this.widget = $( "#station-template" ).clone();
    this.widget.css( "display", "block" );
    this.widget.removeAttr( "id" );
    $( "#station-list" ).append( this.widget );
    if (url)
        $("input", this.widget).val(url);
    this.setLabel((index + 1) + " - ");
}
