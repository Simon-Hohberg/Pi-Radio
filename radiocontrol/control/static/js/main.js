var stationList;
var radio;
var view;

$(function() {
    $( "#tabs" ).tabs();
    $( "#play" ).button({
        icons: { primary: "ui-icon-play" },
        text: false
    });
    
    radio = new Radio();
    view = new ControlsView(radio);
    
    $( "#play" ).click( function() {
        if (radio.isPlaying) {
            stop( function() {
                radio.stopped();
                view.stopped();
            });
        } else {
            play( function(state) {
                radio.playing(state.station);
                view.playing();
            });
        }
    });
    
    // start polling the radio state and system info
    window.setInterval("getRadioState(updateRadioState)", 2000);
    window.setInterval("getSystemInfo(updateSystemInfo)", 5000);
    
    getStationList(function(data) {
        stationList = new StationList(data);
    }, function() {
        // TODO error handling
    });
    
    
});


function updateRadioState(data) {
    if (data.station != "") {
        radio.playing(data.station);
        view.playing();
    } else {
        radio.stopped();
        view.stopped();
    }
    console.log(data.volume);
}

function updateSystemInfo(data) {
    view.setSystemInfo(data);
}
