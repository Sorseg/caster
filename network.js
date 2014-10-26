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
        var address = 'ws://sorseg.ru:7778';
        if (document.location.protocol == 'file:'){
            address = 'ws://127.1:7778';
        }
        log("Connecting to "+address)
        self.ws = new WebSocket(address);
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
                
            case 'error':
                view.error(msg.msg)
                break;
                
            case 'environment':
                game_controller.update_terrain(msg);
				break;
                
            case 'walk':
                game_controller.creature.coords = $.map(msg.to, function(val){return parseInt(val)});
                view.update_creature();
                break;
                
            case 'event':
                game_controller['do_'+msg.type](msg);
                break;
                
            case undefined:
                log("Undefined message type:"+" "+JSON.stringify(msg))
                break;
                
            default:
                log("Unknown message type:"+message_type+" "+JSON.stringify(msg))
                break;
        }
    }
    
    self.login = function(login, password){
        game_controller.state = STATE_LOGGING_IN;
        view_update_status();
        self.ws.send(JSON.stringify({what:"login", login: login, password: password})); 
    }
    
}
