
/**
 * Radio model
 */
function Radio() {
    var self = this;
    
    this.isPlaying = false;
    this.station = null;
    
    this.stopped = function() {
        self.isPlaying = false;
        self.station = null;
    };
    
    this.playing = function(station) {
        self.isPlaying = true;
        self.station = station;
    };
    
}
