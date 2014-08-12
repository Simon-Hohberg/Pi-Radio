
// --------------------------- same origin handling ---------------------------
var csrftoken;

$(function() {
    csrftoken = $.cookie("csrftoken");
});

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


// ------------------------------- radio state --------------------------------

function getRadioState(callback) {
    $.get(
        "radioState/",
        {},
        callback
    );
}


// ------------------------------- radio control -------------------------------

function play(callback) {
    $.get(
        "play/",
        {},
        callback
    );
}

function stop(callback) {
    $.get(
        "stop/",
        {},
        callback
    );
}


// --------------------------------- stations ---------------------------------

function getCurrentStation(callback) {
    $.get(
        "currentStation",
        {},
        callback
    );
}

function getStationList(callback, onError) {
    $.get(
        "stationList",
        {},
        callback
    ).fail(onError);
}

function sendStationList(stations, onError) {
    $.post(
        // important: trailing slash for POST
        "updateStationList/",
        JSON.stringify(stations),
        "json"
    ).fail(onError);
}
