function ControlsView(radio) {
    var self = this;
    this.radio = radio;
    this.playButton = $( "#play" );
    this.banner = $("#info-text");

    this.offline = $( "#internet-connection" );
    this.cpuFreq = $( "#cpu-freq" );
    this.cpuTemp = $( "#cpu-temp" );

    this.volume = 0;

    this.applyStaionListButton = $( "#apply-station-list-button" ).button({
        icons: {
            primary: "ui-icon-check"
        },
        text: true
    });
    this.resetStaionListButton = $( "#reset-station-list-button" ).button({
        icons: {
            primary: "ui-icon-arrowreturnthick-1-e"
        },
        text: true
    });

    this.addStationButton = $( "#add-station-button" ).button({
        icons: {
            primary: "ui-icon-plus"
        },
        text: false
    });

    this.applyStaionListButton.click(function(event) {
        var stations = stationList.toArray();
        sendStationList(stations, function(){
            // TODO error handling
        });
    });

    this.resetStaionListButton.click(function(event) {
        getStationList(function(data) {
            stationList.reload(data);
        }, function() {
            // TODO error handling
        });
    });

    this.addStationButton.click(function(event) {
        stationList.addStation("", "");
    });

    
    this.playing = function() {
        self.playButton.button({
                      icons: { primary: "ui-icon-pause" },
                      text: false
                });
        self.banner.text("// Now Playing // " + self.radio.station);
    };
    
    this.stopped = function() {
        self.playButton.button({
                      icons: { primary: "ui-icon-play" },
                      text: false
                });
        self.banner.text("// Radio stopped //");
    };

    this.setSystemInfo = function(sysInfo) {
        if (sysInfo["offline"]) {
            self.offline.text("Offline");
        } else {
            self.offline.text("Online");
        }
        self.cpuFreq.text(sysInfo["current"]);
        self.cpuTemp.text(sysInfo["temp"]);
    };

    this.setVolume = function(volume) {
        this.volume = volume;
    };
}
