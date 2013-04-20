var approx_maps = [
	[],
	[[0, 0]],
	[[0, 0], [0, 1], [1, 0], [1, 1]],
	[[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]],
	[[0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [1, 3], [2, 0], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2]],
	[[0, 1], [0, 2], [0, 3], [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3]]]


var anim_length = 200;
var ws = new WebSocket('ws://'+document.location.host);
var joined_crid;
var game_state;
var objects = {};
var creatures;
var zero_pad = "0000";

function pad_with_zeroes(coord){
	return (zero_pad+coord).slice(-zero_pad.length)
}

function make_str_coord(coord){
	return pad_with_zeroes(coord[0])+":"+pad_with_zeroes(coord[1])
}

var populate = function(crtr){
     tabBody=document.getElementById("creatures");
     row=document.createElement("TR");
     cell_id = document.createElement("TD");
     cell_cls = document.createElement("TD");
     cell_name = document.createElement("TD");
     cell_use = document.createElement("BUTTON");
     cell_use.innerText = "JOIN";
     cell_use.onclick = function(){
     	ws.send(JSON.stringify(
     		{"what":"join",
     		 "crid":crtr.id
     		}
     ));
     }
     textnode_id=document.createTextNode(crtr.id);
     textnode_cls=document.createTextNode(crtr.cls);
     textnode_name=document.createTextNode(crtr.name);
     cell_id.appendChild(textnode_id);
     cell_cls.appendChild(textnode_cls);
     cell_name.appendChild(textnode_name);
     row.appendChild(cell_id);
     row.appendChild(cell_cls);
     row.appendChild(cell_name);
     row.appendChild(cell_use);
     tabBody.appendChild(row);
}
ws.onmessage = function(message) {
	document.getElementsByName('output')[0].value += message.data+'\n';
	var obj = JSON.parse(message.data)
	switch(obj.what){
	
	case "login":
		$('#login_form').hide(anim_length);
		creatures = Array();
		obj.creatures.map(function(crtr){
			creatures[crtr.id] = crtr;
			populate(crtr)});
			
		$('#creatures').show(anim_length);
		break;
		
	case "joined":
		$('#creatures').hide(anim_length);
		$('#cr_info').show(anim_length);
		$('#cr_name').html(creatures[obj.crid].name);
		joined_crid = obj.crid;
		break;
		
	case "environment":
		map = {};
		object_map = {};
		coords = [];
		
		obj.cells.map(function(cell){
			
			text_coords = make_str_coord(cell.coords);
			coords.push(text_coords)
			map[text_coords] = cell;
		});
		coords.sort();
		
		mincoord = coords[0].split(':');
		map.xmin = parseInt(mincoord[0]);
		map.ymin = parseInt(mincoord[1]);
		
		maxcoord = coords[coords.length-1].split(':');
		map.xmax = parseInt(maxcoord[0]);
		map.ymax = parseInt(maxcoord[1]);
		obj.objects.map(function(o){
			approx_maps[o.size].map(
				function(c){
					object_map[make_str_coord([c[0]+o.coords[0], c[1]+o.coords[1]])] = o;
				}
			);
			objects[o.id] = o;
		});
		str = "";
		models = {"kob1":"@",
		          "drak1":"&",
		          "sword":")",
		          "wall":"#",
		          "floor":"." };
		for(var y = map.ymin; y<=map.ymax; y++){
			str += "<tr>";
			for(var x = map.xmin; x<=map.xmax; x++){
				str_coord = make_str_coord([x,y])
				if(str_coord in object_map){
					o = object_map[str_coord];
					ch = models[o.model];
					cls = "object";
					if (o.id == joined_crid){
						cls += " my_cr";
					}
					str += '<td class="'+cls+'", oid='+o.id+' >'+ch +'</td>';
				} else if(str_coord in map){
					t = map[str_coord];
					ch = models[t.type];
					str += '<td xpos="'+x+'" ypos="'+y+'" t_type="'+t.type+'" >'+ch+'</td>';
				} else {
					str += '<td class="t_undef"> </td>';
				}
			}
			str += '</tr>';
		}
		
		$("#field").html(str);
		$("#game_turn").html(obj.turn);
		break;
		
	case "responses":
		//TODO: register enter/exit
		$("#game_turn").html(obj.turn+1);
		break;
		
	}
};
ws.onclose = function(){
	document.getElementsByName('output')[0].value += "DISCONNECTED\n";
}
function do_login(form)
{
	f = document.getElementById('login_form')
	ws.send(JSON.stringify({what:"login", 
	                        login:f.login.value,
	                        passw:f.passw.value}))
	return false;
}

$(function(){
	$('body').on('click','#field td', function(e){
		xpos = e.toElement.getAttribute('xpos')
		ypos = e.toElement.getAttribute('ypos')
		//alert(xpos+", "+ypos);
	});
	
	function update_info(){
		var hoof = $('.object_hovered');
		var sel = $('.object_selected');
		obj = false;
		if (hoof.length != 0){
			obj = objects[hoof.attr('oid')]
		} else if (sel.length != 0) {
			obj = objects[sel.attr('oid')]
		}
		if (obj == false){
			str = 'Nothing selected';
		} else {
			str = "<ul>";
			for (var p in obj){
				str += '<li>'+p+' — '+obj[p]+'</li>';
			}
		}
		$('#target_description').html(str);
	}
	
	function get_td_by_object(o){
		return $('td[oid="'+$(o).attr('oid')+'"]');
	}
	
	$('#field').on('mouseenter mouseleave','td.object', function(){
		get_td_by_object(this).toggleClass('object_hovered');
		update_info();
	});
	
	$('#field').on('click','td.object', function(){
		get_td_by_object(this).toggleClass('object_selected');
		$('.object_selected').not('[oid='+$(this).attr('oid')+']').removeClass('object_selected');
		update_info();
		
	});
	
	
});