function Station(index, uri) {
    var self = this;
    
    this.setLabel = function (text) {
        $( "label", this.widget ).text( text );
    };
    
    this.remove = function () {
        this.widget.remove();
    };
    
    this.setOnRemoveListener = function (listener) {
        $( "button", this.widget ).click( function ( event ) {
            listener(self.index);
        });
    };
    
    this.getURI = function() {
        return $("input", this.widget).val();
    };
    
    this.index = index;
    
    this.widget = $( "#station-template" ).clone();
    this.widget.css( "display", "block" );
    this.widget.removeAttr( "id" );
    $( "#station-list" ).append( this.widget );
    if (uri)
        $("input", this.widget).val(uri);
    // TODO add on change listener or introduce "apply" button
    this.setLabel((index + 1) + " - ");
}