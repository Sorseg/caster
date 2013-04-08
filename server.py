#!/usr/bin/python3.3

import tornado.ioloop
import tornado.web
import tornado.websocket
import logic
import commands
import logging
import uuid
import json

logging.basicConfig(filename='caster.log', level=logging.DEBUG)

class Player:
    players = {}
    
    def __init__(self):
        self.login = None
    
    def joined(self):
        if self.creature:
            return True
        return False
    

class MainHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.player = Player()

    def on_message(self, message):
        commands.do(self, message)

    def on_close(self):
        #TODO: logout
        pass
    
    def send_json(self, msg):
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        self.write_message(msg)
    

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':'./static'}),
],
    debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()