#!/usr/bin/python3.3

import tornado.ioloop
import tornado.web
import tornado.websocket
import logic
import commands
import logging
import uuid

logging.basicConfig(filename='caster.log', level=logging.DEBUG)

class MainHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.login = None

    def on_message(self, message):
        commands.do(self, message)

    def on_close(self):
        #TODO: logout
        pass
    

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':'./static'}),
],
    debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()