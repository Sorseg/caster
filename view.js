
atom.declare( 'Caster.View',
	{
		anim_length : 300,
		
		initialize: function(controller){
			this.controller = controller;
		},
		
		fill_creature_table: function(crtrs){
			tabBody=$("#creatures tbody").first();
			crtrs.map(function(crtr){
				row = "<tr><td>"+crtr.id+
					  "</td><td>"+crtr.cls+
					  "</td><td>"+crtr.name+
					  '</td><td><button crid="'+crtr.id+'" onclick="caster_controller.network_controller.do_join(this);" >JOIN</button></td></tr>';
				tabBody.append(row);
			});
		},
		
		connect: function(){
			$('#connect_button').stop().hide(this.anim_length);
			$('#login_form').stop().show(this.anim_length);
		},
		
		message: function(message){
			$('#console_output').append(message.data+'\n');
		},
		
		disconnected: function(){
			$('#console_output').append('DISCONNECTED\n');
			$('#creatures').stop().hide(this.anim_length);
			$('#cr_info').stop().hide(this.anim_length);
			$('#login_form').stop().hide(this.anim_length);
			$('#connect_button').stop().show(this.anim_length);
		},
		
		login: function(obj){
			$('#login_form').stop().hide(this.anim_length);
			$('#creatures tbody').html('');
			this.fill_creature_table(obj.creatures);
			$('#creatures').stop().show(this.anim_length);
		},
		
		joined: function(obj){
			$('#creatures').stop().hide(this.anim_length);
			$('#cr_info').stop().show(this.anim_length);
			$('#cr_name').html(obj.name);
		},
		
		update_turn_n: function(n){
			$('#game_turn').html(n);
		},
		
		update_coords: function(c){
			$('#pointer_coords').html(c.x+", "+c.y);
		},
		
		toggle_action: function(b){
			var s = $(b).hasClass('selected');
			
			if(!s){
				this.controller.action = $(b).val();
				$('button.action').removeClass('selected');
				$(b).addClass('selected');
			} else {
				this.reset_action();
			}
			

		},
		
		reset_action: function(){
			this.controller.action = 'select';
			$('button.action').removeClass('selected');
			$('button.action[value=select]').addClass('selected');
		},
		
		remove_request: function(req){
			//if req already deleted: return
			//else call this.controller.remove_request(req);
		}
		
	}
);
