"use strict";


var STATE_CONNECTED = 'Connected',
    STATE_DISCONNECTED = 'Disconnected',
    STATE_CONNECTING = 'Connecting...';


var EVENT_CONNECTED = 'network.connected',
    EVENT_CONN_LOST = 'network.disconnected';


function NetworkClient(){
    
    var _this = this;
    _this.ws = null;
    _this.state = STATE_DISCONNECTED;

    _this.set_state = function(state){
        _this.state = state;
    }
    
    _this.get_state = function(){
        return _this.state;
    }
    
    _this.connect = function(){
        _this.state = STATE_CONNECTING;
        try {
            this.ws.close();
        } catch(e) {}
        _this.ws = new WebSocket('ws://127.1:7778');
        _this.ws.onopen = function(){
            _this.state = STATE_CONNECTED;
            trigger_event(EVENT_CONNECTED);
        }
        _this.ws.onmessage = function(evt){	_this.dispatcher(JSON.parse(evt.data)) };
        _this.ws.onerror = function(evt){console.error(evt)};
    };
    
    _this.dispatcher = function(msg){
        switch(msg.what){
            case 'creature':
                var creature = new PlayerCreature();
                creature.name = msg.name
                trigger_event(EVENT_LOGIN, creature);
            break;
        }
    }
    
    _this.login = function(login, password){
        game_controller.state = STATE_LOGGING_IN;
        _this.ws.send(JSON.stringify({what:"login", login: login, password: password})); 
    }
    
}


function MockNetworkClient(){
    
    var this_ = this;
    
    this_.state = STATE_DISCONNECTED;
    
    this_.set_state = function(state){
        this_.state = state;
    }
    
    this_.get_state = function(){
        return this_.state;
    }
    
    this_.connect = function(){
        this_.state = STATE_CONNECTING;
        setTimeout(function(){
            this_.state = STATE_CONNECTED;
            trigger_event(EVENT_CONNECTED);
        }, 500);
    };
    
    this_.login = function(){
        game_controller.state = STATE_LOGGING_IN;
        setTimeout(function(){
            var player = new Player();
            
            trigger_event(EVENT_LOGIN);
        }, 500);
    }
    
    log("Mock controller initialized");
}

//var NetworkClient = MockNetworkClient;

/*
var ws;
var joined_crid;
var STATE_CONNECTED = 'connected',
    STATE_DISCONNECTED = 'disconnected'

var connection_state = STATE_DISCONNECTED;

function connect(){
    if (connection_state == STATE_CONNECTED){
        throw "Already Connected";
    }
    ws = new WebSocket('ws://sorseg.ru/caster');
}

$(function(){
    connect();
});


atom.declare('Caster.Network', {
	
	initialize: function(controller){
		this.controller = controller;
		this.bindMethods(['digest'])
	},
	
	connect: function(){
		this.controller.view.connect();
		
		this.ws = new WebSocket('ws://'+document.location.host);
		this.ws.onmessage = this.digest.bind(this);
		this.ws.onclose = this.controller.view.disconnected;
	},
	
	digest:	function(message) {
		this.controller.view.message(message);
		
		var obj = JSON.parse(message.data);
		if(!this.controller.reactions.contains(obj.what)){
			console.log("Failed to digest "+obj.what+", it is not in reactions");
			return;
		}
		
		this.controller[obj.what](obj);
		return;
		
	},

	do_login: function (form)
	{
		var f = document.getElementById('login_form')
		this.send({what:"login", 
								login:f.login.value,
								passw:f.passw.value});
		return false;
	},

	do_join: function(button){
		this.send(
		 		{"what":"join",
		 		 "crid":parseInt(button.getAttribute("crid"))
		 		}
		 );
	},
	
	send: function(msg){
		this.ws.send(JSON.stringify(msg));
	}


})
*/