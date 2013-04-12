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


def locking(loc_id):
    def wrapper(func):
        @EXECUTOR.submit
        def job():
            with loc_locks[loc_id]:
                try:
                    func()
                except:
                    logging.exception("Error in locking function")
    return wrapper


def send_environment(player):
    #TODO: something if location of creature changes
    id = player.creature.loc_id or player.loc_id
    @locking(id)
    def _():
        with db.Handler() as h:
            logging.info("ID OF LOCATION: {!s}".format(id))
            
            loc = h.session.query(db.Location).get(id)
            env = dict(what = "environment",
                       location = id,
                       turn = loc.current_turn,
                       )
            env['cells'] = [c.info() for c in loc.cells.values()]
            env['objects'] = [o.info() for o in loc.objects.values()]
            logging.info("Sending env")
            player.handler.send_json(env)
            
        
        

def add_updater(loc_id):
    upd = tornado.ioloop.PeriodicCallback(create_loc_updater(location.id), 1000*TIMEOUT, loop)
    loc_updaters[location.id] = upd
    upd.start()

def check_update(player):
    '''TODO: Add updater as soon as player enters location
    '''
    if player.loc_id not in loc_updaters:
        add_updater(player.loc_id)
    
def create_loc_updater(id):
    def updater():
        @locking(id)
        def _():
            with db.handler() as h:
                logging.info("updating", id)
                l = h.query(db.Location).get(id)
                logging.info("Turn #{}".format(l.current_turn))
                for r in loc_requests[id]:
                    logging.debug("Processing {!s}".format(r))
                l.current_turn += 1
            
    return updater
    
def init(loop):
    with db.Handler() as h:
        for location in h.session.query(db.Location):
            if location.creatures:
                add_updater(location.id)


                