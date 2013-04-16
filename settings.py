
######  SERVER SETTINGS:  ###########

LISTEN_PORT = 8888
TCP_LISTEN_PORT = 8889
import logging
logging.basicConfig(filename='caster.log', level=logging.DEBUG)


######  GAME SETTINGS:  #############

TURN_TIMEOUT = 20

#####  MISC:  #############

#DATABASE_CONNECTION = 'mysql+mysqlconnector://caster:sejf3sjdijoR5EVIOJ@localhost/caster'
DATABASE_FILE_NAME = 'db.db'
DATABASE_CONNECTION = 'sqlite:///'+DATABASE_FILE_NAME
