#!/usr/bin/python3.3
'''
TODO:
- connection timeout
'''
import asyncio

import websockets
from operator import attrgetter
import logging
import sys
logging.basicConfig(stream=sys.stdout)
json_default = attrgetter('id')



input = []


@asyncio.coroutine
def handler(proto, uri):

    @asyncio.coroutine
    def reader():
        while proto.open:
            print(repr((yield from proto.recv())))

    @asyncio.coroutine
    def writer():
        while proto.open:
            yield from proto.send("PING")
            yield from asyncio.sleep(2)

    print("CONNECTED TO", uri)
    yield from asyncio.wait([writer(), reader()])
    print("DONE")


asyncio.get_event_loop().run_until_complete(websockets.serve(handler, 'localhost', 7778))
asyncio.get_event_loop().run_forever()


