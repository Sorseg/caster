import logging
import json
import database as db
import logic
import requests

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

def do(handler, actions):
    try:
        js = json.loads(actions)
        if not type(js) is list:
            js = [js]
        for action in js:
            cmd = action.pop('what')
            if cmd.upper() not in commands:
                handler.write_message(error("No such command:{} "
            "please refer to "
            "https://code.google.com/p/caster/wiki/casterJsonProtocol"
            .format(cmd), actions = actions))
                return
            commands[cmd.upper()](handler, **action)
    except Exception as e:
        logging.exception("omg")
        handler.write_message(server_error(repr(e), actions = actions))
        
#COMMANDS:

@cmd
def login(handler, login, passw):
    player = handler.player 
    send = handler.write_message
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
        
        if login in player.players:
            send(fail("Already logged in"))
            return
        player.login = login
        player.players[login] = player
        player.creatures = {c.id:c for c in creatures}
        
        send({"what":"login",
              "creatures":[c.short_info for c in creatures]})

@cmd
def join(handler, crid):
    player = handler.player
    with db.Handler() as h:
        player.creature = h.refresh(player.creatures[crid])
        if any( c == None for c in player.creature.coords):
            requests.ENTER(player, 1)
        logic.send_environment(player)

@cmd 
def request(handler):
    pass
