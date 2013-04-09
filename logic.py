from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from threading import RLock
import database as db
import tornado.ioloop
import logging

EXECUTOR = ThreadPoolExecutor(max_workers=4)
TIMEOUT = 15

loc_locks = defaultdict(RLock)
loc_updaters = {}
loc_requests = defaultdict(list)


def locking(loc_id, can_cancel = True):
    def wrapper(func):
        @EXECUTOR.submit
        def job():
            with loc_locks[loc_id]:
                func()
    return wrapper


def send_environment(player):
    pass

def check_update(player):
    '''TODO: Add updater as soon as player enters location
    '''
    
def update_loc(id):
    def updater():
        #TODO:
        logging.info("updating", id)
    return updater
    
    
def init(loop):
    with db.Handler() as h:
        for location in h.session.query(db.Location):
            if location.creatures:
                upd = tornado.ioloop.PeriodicCallback(update_loc(location.id), 1000*TIMEOUT, loop)
                loc_updaters[location.id] = upd
                upd.start()

                