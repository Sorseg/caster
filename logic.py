from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from threading import RLock
import database as db
import tornado.ioloop
import logging

EXECUTOR = ThreadPoolExecutor(max_workers=4)
TIMEOUT = 15
MAX_TIME = 100

loc_locks = defaultdict(RLock)
loc_updaters = {}
loc_requests = defaultdict(list)
loc_responses = defaultdict(list)

logic_functions = {}


class Player:
    players = {}
    
    def __init__(self, handler):
        self.handler = handler
        self.login = None
        self.loc_id = -1
    
    def joined(self):
        if self.creature:
            return True
        return False
    
    @classmethod
    def get_players(cls, loc_id):
        return [p for p in cls.players.values() if p.loc_id == loc_id]


def logic(func):
    ''' Registers function as action,
    which can be performed with request
    '''
    logic_functions[func.__name__.lower()] = func
    return func


def locking(loc_id):
    if not loc_id:
        raise ValueError("No loc_id to lock")
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
            loc = h.session.query(db.Location).get(id)
            env = dict(what = "environment",
                       location = id,
                       turn = loc.current_turn,
                       )
            env['cells'] = [c.info() for c in loc.cells.values()]
            env['objects'] = [o.info() for o in loc.objects.values()]
            player.handler.write_message(env)
            
def add_updater(loc_id, loop = None):
    args = [create_loc_updater(loc_id), 1000*TIMEOUT]
    if loop:
        args.append(loop)
    upd = tornado.ioloop.PeriodicCallback(*args)
    loc_updaters[loc_id] = upd
    upd.start()

def check_update(player):
    '''TODO: Add updater as soon as player enters location
    '''
    if player.loc_id not in loc_updaters:
        add_updater(player.loc_id)
        
def create_response(request, success = True, **kw):
    response = {"what":"response",
                "result":"success" if success else "fail"}
    for k in ['type', 'source', 'target', 'target_cell', 'time', 'duration']:
        if k in request:
            response[k] = request[k]
    response.update(kw)
    loc_responses[request['loc_id']].append(response)
    
def create_loc_updater(id):
    def updater():
        @locking(id)
        def _():
            logging.debug("Updating location #{}".format(id))
            requests = loc_requests.pop(id, [])
            
            current_times = defaultdict(int)
            for r in requests:
                s = r['source']
                new_time = current_times[s.id] + r['duration']
                
                if new_time > MAX_TIME:
                    create_response(r, success = False)
                r['time'] = current_times[s.id]
                current_times[s.id] += r['duration']
                
            requests = sorted(requests, key = lambda r: r['time'])
            #TODO: implement simultaneous actions
            for r in requests:
                try:
                    logic_functions[r['type']](r)
                except:
                    logging.exception("Error in logic function")
                logging.debug("Processing {!s}".format(r))
            with db.Handler() as h:
                l = h.get_location(id)
                responses = loc_responses.pop(id ,[])
                resp_json = {"what":"responses", "responses" : responses, "turn":l.current_turn}
                l.current_turn += 1
                logging.info("Planning turn #{}".format(l.current_turn))
            for p in Player.get_players(id):
                p.handler.write_message(resp_json)
            
    return updater
    
def init(loop):
    with db.Handler() as h:
        for location in h.session.query(db.Location):
            if location.creatures:
                add_updater(location.id, loop)


######################### LOGIC ROUTINES ######################

@logic
def enter(request):
    logging.debug("ENTERING...")
    with db.Handler() as h:
        l = h.get_location(request['loc_id'])
        s = h.refresh(request['source'])
        for cell in l.cells:
            space = s.space()
            if space.fits(cell, l):
                s.coords = cell
                s.loc_id = l.id
                create_response(request, target_cell = cell)
                break
        else:
            create_response(request, success = False)
            #TODO: Tell user and try again
        

                