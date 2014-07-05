function hide_element(el){
    el.addClass('hidden');
}

function show_element(el){
    el.removeClass('hidden');
}

var log = function(msg){
    $('#console_output').append(msg+'\n')
};

function on_connection(){
    hide_element($('#connect_button_wrapper'));
    show_element($('#login_form'));
}

function on_connection_lost(){
    show_element($('#connect_button_wrapper'));
    //TODO: game board disconnected overlay
}

function on_login(character){
    //TODO: update gui according to character;
    game_controller.state = STATE_LOGGED_IN;
    hide_element($('#login_form'));
    show_element($('#game_board'));
    localStorage.setItem('username', $('#login').val());
}

$(function(){
    
    register_event(EVENT_LOGIN, on_login);
    register_event(EVENT_CONNECTED, on_connection);
    register_event(EVENT_CONN_LOST, on_connection_lost);

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
    
    function update_status(){
        $('#game_status').text(game_controller.state);
        $('#connection_status').text(network_client.state);
    }
    
    setInterval(update_status, 200);
    $('#connect_button').click();
    
});