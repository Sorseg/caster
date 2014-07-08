"use strict";


var STATE_CONNECTED = 'Connected',
    STATE_DISCONNECTED = 'Disconnected',
    STATE_CONNECTING = 'Connecting...';


var EVENT_CONNECTED = 'network.connected',
    EVENT_CONN_LOST = 'network.disconnected';


function NetworkClient(){
    
    var self = this;
    self.ws = null;
    self.state = STATE_DISCONNECTED;
    
    self.connect = function(){
        self.state = STATE_CONNECTING;
        try {
            this.ws.close();
        } catch(e) {}
        self.ws = new WebSocket('ws://127.1:7778');
        self.ws.onopen = function(){
            self.state = STATE_CONNECTED;
            trigger_event(EVENT_CONNECTED);
        }
        self.ws.onmessage = function(evt){
            //console.log("MSG:"+evt.data);
            self.dispatcher(JSON.parse(evt.data));
        };
        self.ws.onerror = function(evt){log("connection error");};
        self.ws.onclose = function(evt){
            self.state = STATE_DISCONNECTED;
            trigger_event(EVENT_CONN_LOST);
        };
    };
    
    self.dispatcher = function(msg){
        var message_type = msg.what;
        delete msg.what;
        switch(message_type){
            case 'creature':
                var creature = new PlayerCreature(msg);
                game_controller.creature = creature;
                trigger_event(EVENT_LOGIN, creature);
                game_controller.state = STATE_LOGGED_IN;
                break;
                
            case 'nocreature':
                if (game_controller.state == STATE_LOGGING_IN){
                    game_controller.state = STATE_LOGGED_OUT;
                    log("No creature found");
                    trigger_event(EVENT_LOGOUT);
                }
                break;
                
            case 'environment':
                game_controller.update_terrain(msg);
				break;
                
            case undefined:
                log("undefined message type:"+msg)
                break;
        }
    }
    
    self.login = function(login, password){
        game_controller.state = STATE_LOGGING_IN;
        view_update_status();
        self.ws.send(JSON.stringify({what:"login", login: login, password: password})); 
    }
    
}