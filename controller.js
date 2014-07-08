"use strict";

var STATE_LOGGED_IN = 'Logged in',
    STATE_LOGGED_OUT = 'Logged out',
    STATE_LOGGING_IN = 'Logging in...';

var EVENT_LOGIN = 'game.login',
    EVENT_LOGOUT = 'game.logout';

var network_client,
    game_controller;

function register_event(evt, fnc){
    $(document).on(evt, fnc);
}

function trigger_event(evt, args){
    console.log("EVENT: "+evt)
    $(document).trigger(evt, args);
    view_update_status();
}

function GameController(){
    this.state = STATE_LOGGED_OUT;
    
    var self = this;
    self.logout = function(){
        self.state = STATE_LOGGED_OUT;
        trigger_event(EVENT_LOGOUT);
    }
    register_event(EVENT_CONN_LOST, self.logout)
}


//////////////////////////// MAIN ////////////////////////

$(function(){
    network_client = new NetworkClient();
    game_controller = new GameController();
});