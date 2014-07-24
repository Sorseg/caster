var view = {}

String.prototype.format = function(vars){
    return this.replace(/{(.*?)}/g, function(m, k){return vars[k]})
}

terr_chars ={
    floor:'&#xb7;',
    wall:'#',
    nothing:""
};

var SIZE = 10;

function hide_element(el){
    el.addClass('hidden');
}

function show_element(el){
    el.removeClass('hidden');
}

function log(msg){
    var co = $('#console_output');
    co.append(msg+'<br>');
    co.scrollTop(co[0].scrollHeight);
}

function view_update_status(){
    setTimeout(function(){  
        $('#connection_status').text(network_client.state);
        $('#game_status').text(game_controller.state);
    }, 50);
}

function on_connection(){
    hide_element($('#connect_button_wrapper'));
    show_element($('#login_form'));
    
}

register_event(EVENT_CONNECTED, on_connection);


function on_connection_lost(){
    show_element($('#connect_button_wrapper'));
    hide_element($('#game_board'));
    hide_element($('#login_form'));
    
}

register_event(EVENT_CONN_LOST, on_connection_lost);


function on_login(evt, creature){
    //TODO: update gui according to character;
    hide_element($('#login_form'));
    show_element($('#game_board'));
    localStorage.setItem('username', $('#login').val());
    $('#character_name').text(creature.name);
    view.update_creature();
}

register_event(EVENT_LOGIN, on_login);


view.terrain_redraw = function(terr, pos){
    var new_table = $('<tbody>');
    for(var y = pos[1]-SIZE; y <= pos[1]+SIZE; y++){
        var line = $('<tr>').attr('posy', y).appendTo(new_table);
        for(var x = pos[0]-SIZE; x <= pos[0]+SIZE; x++){
            var point = terr[""+x+","+y];
            var cell = $('<td>').attr('posx', x).appendTo(line);
            var div = $('<div>').appendTo(cell);
            
            if (typeof point != 'undefined'){
                if((sq_dist([x, y], pos) <= 2) &&
                   (sq_dist([x, y], pos) > 0) &&
                   (point[3] == 'floor')){
                    cell.addClass("walkable");
                }
                cell.css("background","rgb("+point.slice(0,3).join(',')+")");
                div.html(terr_chars[point[3]]);
            }
        }
    }
    $('#field').html(new_table);
    view.place(pos[0], pos[1], '@');
    //$('#field tr[posy={y}] td[posx={x}] div'.format({x:pos[0], y:pos[1]})).text('@');
}

view.update_creature = function(){
    $('#character_position').text(game_controller.creature.coords);
}

function sq_dist(p1, p2){
    var dx = p2[0] - p1[0];
    var dy = p2[1] - p1[1];
    return dx*dx+dy*dy;
}


view.get_coords = function(td){
    var x = td.attr('posx');
    var y = td.parent().attr('posy');
    return [x, y];
}

view.place = function(x, y, char){
    $('#field tr[posy={y}] td[posx={x}] div'.format({x:x, y:y})).text(char);
}

view.error = function(err){
    var span = $('<span>').addClass('red');
    span.text(err);
    $('#console_output').append(span).append('<br>');
}

view.draw_objects = function(objects){
    $.each(objects,function(coord, obj){
        c = $.map(coord.split(','), function(i){return parseInt(i)});
        view.place(c[0], c[1], 'z');
        log(c);
    });
        
}



$(function(){
    hide_element($('#game_board'));
    hide_element($('#login_form'));
    
    var username = localStorage.getItem('username') || "User";
    
    $('#login').val(username);
    
    $('#connect_button').click(function(evt){
        evt.preventDefault();
        network_client.connect();
    });
    
    $('#login_button').click(function(evt){
        evt.preventDefault();
        network_client.login(
            $('#login').val(),
            $('#passw').val());
    });
    
    $('#connect_button').click();
    
    $('#field').on('click', 'td', function(evt){
        var td = $(evt.target).parents('td');
        if(td.hasClass('walkable')){
            game_controller.walk(view.get_coords(td));
        }
    });
    
});

