#!/usr/bin/python3.3
'''
TODO:
- connection timeout
'''
from settings import *
from tornado.tcpserver import TCPServer
import commands
import json
import logging
import logic
import sys
import tornado.ioloop
import tornado.web
import tornado.websocket
from operator import attrgetter

json_default = attrgetter('id')

class MainHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.player = logic.Player(self)

    def on_message(self, message):
        logging.debug("Message: "+message)
        commands.do(self, message)

    def on_close(self):
        logic.Player.players.pop(self.player.login, None)
        
    def write_message(self, msg):
        if isinstance(msg, dict):
            msg = json.dumps(msg, default = json_default)
        return super().write_message(msg)


class SocketServer(TCPServer):
    
    def handle_stream(self, stream, addr):
        logging.info("Connection from {!r}".format(addr))
        stream.player = logic.Player(stream)
        
        def write_message(msg):
            stream.write(bytes(json.dumps(msg, default = json_default), 'utf8') + b'\n')    
        stream.write_message = write_message
        
        def on_close():
            logic.Player.players.pop(stream.player.login, None)
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
    application.listen(LISTEN_PORT)
    loop = tornado.ioloop.IOLoop.instance()
    logic.init(loop)
    server = SocketServer()
    server.bind(TCP_LISTEN_PORT)
    server.start()
    logging.info("Server started")
    loop.start()
