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
from tornado.tcpserver import TCPServer
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


class SocketServer(TCPServer):
    
    def handle_stream(self, stream, addr):
        logging.info("Connection from {!r}".format(addr))
        stream.player = Player(stream)
        
        def write_message(msg):
            stream.write(bytes(json.dumps(msg),'utf8')+b'\n')    
        stream.write_message = write_message
        
        def on_close():
            Player.players.pop(stream.player.login, None)
        stream.set_close_callback(on_close)
        
        def on_message( msg = None):
            if msg != None:
                logging.debug("Sockets message: {!s}".format(msg))
                commands.do(stream, msg.decode('utf8'))
            stream.read_until(b'\n', on_message)
            
        on_message()
    
        

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':'./static'}),
],
    debug=True)

if __name__ == "__main__":
    application.listen(8888)
    loop = tornado.ioloop.IOLoop.instance()
    logic.init(loop)
    server = SocketServer()
    server.bind(8889)
    server.start()
    logging.info("Server started")
    loop.start()
