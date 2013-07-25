$(function() {

    // start polling the radio state
    window.setInterval("getRadioState(updateRadioState)", 5000);

});


function getRadioState(callback) {
    $.get(
        "radioState",
        {},
        callback
    );
}


function updateRadioState(data) {
    if (data.station != "")
        $("#info-text").text("// Now Playing // " + data.station);
    else
        $("#info-text").text("// Radio stopped //");

    // $("#volume").text("Now Playing: " + data.station)
}


function getCurrentStation(callback) {
    $.get(
        "currentStation",
        {},
        callback
    );
}


function getVolume() {

}


function play() {
    $.get(
        "play",
        {},
        playCallback
    );
}


function playCallback(data) {
    $( "#play" ).button({
          icons: { primary: "ui-icon-pause" },
          text: false
    });
    $( "#play" ).click(stop);
}


function stop() {
    $.get(
        "stop",
        {},
        stopCallback
    )
}

function stopCallback(data) {
    $( "#play" ).button({
          icons: { primary: "ui-icon-play" },
          text: false
    });   
    $( "#play" ).click(play);
}


function addStation(station) {

}


function removeStation(stationNo) {

}
