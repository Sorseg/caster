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
    self.objects = {};
    self.creature = null;
    
    self.logout = function(){
        self.state = STATE_LOGGED_OUT;
        self.terrain = {};
        self.objects = {};
        trigger_event(EVENT_LOGOUT);
    }
    register_event(EVENT_CONN_LOST, self.logout)
    
    self.update_terrain = function(terr){
        var objects = terr.objects;
        delete terr.objects;
        $.extend(self.terrain, terr);
        $.extend(self.objects, objects);
        view.terrain_redraw(self.terrain, self.creature.coords);
        view.draw_objects(self.objects);
    }
    
    self.walk = function(coords){
        network_client.ws.send(JSON.stringify({
            what:"action",
            type:"walk",
            where:coords
        }))
    }
    
    self.do_death = function(msg){
        delete self.objects[msg.who];
        view.terrain_redraw(self.terrain, self.creature.coords);
    }
    
    self.attack = function(id){
        network_client.ws.send(JSON.stringify({
            what:"action",
            type:"attack",
            who:id
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