function ControlsView(radio) {
    var self = this;
    this.radio = radio;
    this.playButton = $( "#play" );
    this.banner = $("#info-text");
    
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
}
