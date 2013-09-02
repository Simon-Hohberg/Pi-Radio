var stationList;
var radio;

$(function() {
    $( "#tabs" ).tabs();
    $( "#play" ).button({
        icons: { primary: "ui-icon-play" },
        text: false
    });
    
    radio = new Radio();
    
    $( "#play" ).click( function() {
        if (radio.isPlaying) {
            stop( function (data) {
                $( "#play" ).button({
                      icons: { primary: "ui-icon-pause" },
                      text: false
                });
                radio.isPlaying = false;
            });
        } else {
            play( function(data) {
                $( "#play" ).button({
                      icons: { primary: "ui-icon-play" },
                      text: false
                });
                radio.isPlaying = true;
            });
        }
    });
    
    // start polling the radio state
    window.setInterval("getRadioState(updateRadioState)", 5000);
    
    getStationList(function(data) {
        // TODO how to handle max?
        stationList = new StationList(data, 10);
    }, function() {
        // TODO error handling
    });
});