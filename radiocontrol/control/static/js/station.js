function Station(index, name, uri) {
    var self = this;

    this.setIndex = function(zeroBasedIndex) {
        this.index = zeroBasedIndex;
        $( "label", this.widget ).text( (zeroBasedIndex + 1) + " - " );
    };

    this.setName = function(text) {
        $( ".radio-name", this.widget ).val( text );
    };

    this.setUri = function(uri) {
        $( ".radio-uri", this.widget ).val( uri );
    };
    
    this.remove = function () {
        this.widget.remove();
    };
    
    this.setOnRemoveListener = function (listener) {
        $( "button", this.widget ).click( function ( event ) {
            listener(self.index);
        });
    };
    
    this.getUri = function() {
        return $(".radio-uri", this.widget).val();
    };
    
    this.getName = function() {
        return $(".radio-name", this.widget).val();
    };

    this.widget = $( "#station-template" ).clone();
    this.widget.css( "display", "block" );
    this.widget.removeAttr( "id" );
    $( "#station-list" ).append( this.widget );
    
    this.setName(name);
    this.setUri(uri);
    
    this.setIndex(index);
}