"use strict";
var log = function(msg){
    $('#console_output').append(msg+'\n')
};

$(function(){
    var network_client = new NetworkClient();
    
    $('#connect_button').click(function(evt){
        evt.preventDefault();
        network_client.connect()
    });
    
    $('#login_button').click(function(evt){
        evt.preventDefault();
        network_client.login(
            $('#login').val(),
            $('#passw').val());
    });
    
    $('#connect_button').click();
    
});