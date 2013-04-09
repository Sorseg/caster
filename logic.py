from concurrent.futures import ThreadPoolExecutor
from threading import RLock
import database as db
from functools import wraps
from collections import defaultdict

EXECUTOR = ThreadPoolExecutor(max_workers=4)

loc_locks = defaultdict(RLock)

def locking(loc_id):
    def wrapper(func):
        @EXECUTOR.submit
        def job():
            with loc_locks[loc_id]:
                func()
    return wrapper


def send_environment(player):
    pass
