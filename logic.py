from concurrent.futures import ThreadPoolExecutor
from threading import RLock
import database
LOCATIONS = list(range(10))

locks = {i:RLock() for i in LOCATIONS}

EXECUTOR = ThreadPoolExecutor(max_workers=4)

def digest(handler, message):
            handler.write_message("ASDF "+message)
