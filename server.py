#!/usr/bin/python3.3
'''
TODO:
- connection timeout
'''
import json
import logging
import sys
import tornado.ioloop
import tornado.web
import tornado.websocket

import commands
import logic

logging.basicConfig(filename='caster.log', level=logging.DEBUG)

class Player:
    players = {}
    
    def __init__(self, handler):
        self.handler = handler
        self.login = None
    
    def joined(self):
        if self.creature:
            return True
        return False
    

class MainHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.player = Player(self)

    def on_message(self, message):
        logging.debug("Message: "+message)
        commands.do(self, message)

    def on_close(self):
        Player.players.pop(self.player.login, None)
    

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':'./static'}),
],
    debug=True)

if __name__ == "__main__":
    application.listen(8888)
    loop = tornado.ioloop.IOLoop.instance()
    logic.init(loop)
    loop.start()
