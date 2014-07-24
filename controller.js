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
    var self = this;
    self.state = STATE_LOGGED_OUT;
    self.terrain = {};
    self.creature = null;
    
    self.logout = function(){
        self.state = STATE_LOGGED_OUT;
        trigger_event(EVENT_LOGOUT);
    }
    register_event(EVENT_CONN_LOST, self.logout)
    
    self.update_terrain = function(terr){
        var objects = terr.objects;
        delete terr.objects;
        log(JSON.stringify(objects));
        $.extend(self.terrain, terr);
        view.terrain_redraw(self.terrain, self.creature.coords);
        view.draw_objects(objects);
    }
    
    self.walk = function(coords){
        network_client.ws.send(JSON.stringify({
            what:"action",
            type:"walk",
            where:coords
        }))
    }
    
    self.login_fail = function(reason){
        if (self.state == STATE_LOGGING_IN){
            log("Login failed: "+reason);
            self.logout();
        }
    }
}


//////////////////////////// MAIN ////////////////////////

$(function(){
    network_client = new NetworkClient();
    game_controller = new GameController();
});