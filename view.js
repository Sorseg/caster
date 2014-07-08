function hide_element(el){
    el.addClass('hidden');
}

function show_element(el){
    el.removeClass('hidden');
}

function log(msg){
    $('#console_output').append(msg+'\n');
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
    //TODO: game board disconnected overlay
    hide_element($('#game_board'));
}

register_event(EVENT_CONN_LOST, on_connection_lost);


function on_login(evt, creature){
    //TODO: update gui according to character;
    hide_element($('#login_form'));
    show_element($('#game_board'));
    localStorage.setItem('username', $('#login').val());
    $('#character_name').text(creature.name);
    $('#character_position').text(creature.coords);
}

register_event(EVENT_LOGIN, on_login);




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
    
});