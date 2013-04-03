#!/usr/bin/python3.3

import tornado.ioloop
import tornado.web
import tornado.websocket
import logic

class MainHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        logic.digest(self, message)

    def on_close(self):
        print ("WebSocket closed")

application = tornado.web.Application([
    (r"/", MainHandler),
],
    debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()