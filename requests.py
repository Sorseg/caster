'''
TODO: rewrite ALL
'''

import database as db
import logging
import commands as cmd
from update_logic import locking, check_update
from collections import namedtuple

# request functions to perform an action
requests = {}

def req(func):
    requests[func.func_name.upper()] = func
    return func

def create_request(**kw):
    db.Location.requests[req['loc_id']].append(kw)


class Request:
    def __init__(self, type_, loc_id, target_turn):
        self.type = type_
        self.loc_id = loc_id
        self.target_turn = target_turn

########### SYSTEM REQUESTS: ###########

def ENTER(player, loc_id, x_y = (None,None)):
    ''' Places character at designated location or if not specified: any free safe location '''
    x,y = x_y

    if not player.joined:
        raise Exception("Not joined trying to enter")

    player.loc_id = loc_id

    @locking("system", loc_id = loc_id)
    def add(lock):
        with db.Handler() as h:
            if x == None or y == None:
                targ_cell = None
            else:
                raise NotImplementedError

            create_request(loc_id = loc_id,
                           type = 'enter',
                           source = player.creature.id,
                           target_cell = targ_cell)
        player.committed = True
        check_update(player)

def EXIT(player):
    ''' removes creature from location '''
    # TODO:


########### REQUESTS: ###########

@req
def MOVE(player, info):
    ''' Moves character in direction '''
    if not player.in_game:
        return
    with db.Handler(True) as h:
        @locking("move", loc_id = player.loc_id)
        def move(lock):
            cre = player.creature
            h.session.add(cre)
            if not cre.cell:
                player.send(cmd.error("You have not yet entered the game"))
                return

            if not info:
                player.send(cmd.error("No direction given for 'move'"))
                return

            if not set(info.lower()) <= set('nswe'):
                player.send(cmd.error("unknown direction given: "+info))
                return
            
            create_request(loc_id = player.loc_id,
                           type = "move",
                           source = player.creature.id,
                           info = info)


@req
def COMMIT(player):
    if not player.in_game:
        return
    @locking("commit", toThread=False, loc_id=player.loc_id)
    def upd(lock):
        player.committed = True
        check_update(player)

@req
def CANCEL(player, n = None):
    ''' cancells n actions '''
    # TODO:

@req
def ATTACK(player, target):
    if not player.in_game:
        return
    player.send(cmd.server_error("not yet implemented"))
    return
    @locking("attack", loc_id = player.loc_id)
    def attack(lock):
        with db.Handler(True) as h:
            cre = player.creature
            h.session.add(cre)
            if not cre.cell:
                player.send(cmd.error("You have not yet entered the game"))
                return
            target_c = cre.location.strid_objects[target]
            create_request(loc_id = player.loc_id,
                           type = "attack",
                           source = player.creature,
                           target = target_c,
                           cost = 19)

@req
def PICK(player, target):
    item = int(target)
    # TODO: check if target in same location as player and is visible
    if not player.in_game:
        return
    @locking("pick", loc_id = player.loc_id)
    def pick(lock):
        with db.Handler(True) as h:
            l = h.get_location(player.loc_id)
            player.creature = h.merge(player.creature)
            items = dict(l.id_items)
            items.update({i.id:i for i in player.creature.inventory})

            if item not in items:
                player.send(cmd.error("No item with ID:"+str(item)))
                return
            create_request(loc_id = player.loc_id,
                           type = "pick",
                           source = player.creature,
                           target = items[item],
                           cost = 12)


@req
def DROP(player, target):
    item = int(target)
    # TODO: check if target in same location as player and is visible
    if not player.in_game:
        return

    @locking("drop", loc_id = player.loc_id)
    def drop(lock):
        with db.Handler() as h:
            h.add(player.creature)
            l = h.get_location(player.loc_id)
            items = dict(l.id_items)
            items.update({i.id:i for i in player.creature.inventory})
            if item not in items:
                player.send(cmd.error("No item with ID:"+str(item)))
                return
            create_request(loc_id = player.loc_id,
                           type = "drop",
                           source = player.creature,
                           target = items[item],
                           cost = 10)

@req
def EQUIP(player, target):
    item = int(target)
    if not player.in_game:
        return
    @locking("equip", loc_id = player.loc_id)
    def equip(lock):
        with db.Handler() as h:
            h.add(player.creature)
            l = h.get_location(player.loc_id)
            items = dict(l.id_items)
            items.update({i.id:i for i in player.creature.inventory})
            if item and item not in items:
                player.send(cmd.error("No item with ID:"+str(item)))
                return
            create_request(loc_id = player.loc_id,
                           type = "equip",
                           source = player.creature.id,
                           target = item)
