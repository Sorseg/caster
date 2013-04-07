import logging
import json
import database as db

def error_sender(severity):
    def sender(reason,**kw):
        dic = {"what":severity,"msg":reason}
        dic.update(kw)
        return dic
    return sender

fail = error_sender("fail")
error = error_sender("error")
server_error = error_sender("server error")

commands = {}

def cmd(func):
    " Registers a function as a command " 
    commands[func.__name__.upper()]=func
    return func  

def do(player, actions):
    try:
        js = json.loads(actions)
        if not type(js) is list:
            js = [js]
        for action in js:
            cmd = action.pop('what')
            if cmd.upper() not in commands:
                player.write_message(error("No such command:{} "
            "please refer to "
            "https://code.google.com/p/caster/wiki/casterJsonProtocol"
            .format(cmd), actions = actions))
                return
            commands[cmd.upper()](player, **action)
    except Exception as e:
        logging.exception("omg")
        player.write_message(server_error(repr(e), actions = actions))
        
#COMMANDS:

@cmd
def login(handler, login, passw):
    player = handler.player 
    send = player.write_message
    if player.login:
        send(error("Already logged in"))
        return
    
    with db.Handler() as h:
        creatures = h.login(login, passw)
        if creatures == None:
            send(fail("Login and/or pass are wrong"))
            return
        elif not creatures:
            send(fail("Login {} has no creatures".format(login)))
            return
        
#@cmd TODO
def join(handler, crid):
    with database.Handler() as h:
        crid = str(crid)
        player.creature = h.session.merge(player.creatures[crid])
        if not player.creature.cell:
            requests.ENTER(player, 1)
        else:
            player.loc_id = player.creature.cell.loc_id
            @update_logic.locking("get env", False, loc_id = player.loc_id)
            def send(lock):
                update_logic.send_environment(player, player.loc_id, h)
        

        