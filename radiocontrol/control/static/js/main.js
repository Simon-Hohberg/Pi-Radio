var stationList;

$(function() {
    $( "#tabs" ).tabs();
    $( "#play" ).button({
        icons: { primary: "ui-icon-play" },
        text: false
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