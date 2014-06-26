/**
 * @author sorseg
 */


var ws;
var joined_crid;

$(function(){
    ws = new WebSocket('ws://sorseg.ru/caster');
});

/*
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