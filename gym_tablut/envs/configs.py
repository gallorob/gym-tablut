import os
import configparser

# __all__ = ['BACKGROUND', 'EMPTY', 'CORNER', 'THRONE', 'KING']

curr_dir = os.path.dirname(__file__)
config_file = os.path.join(curr_dir, 'configs.ini')

config = configparser.ConfigParser()
config.read(config_file)

# tile values
BACKGROUND = config['TILES'].getint('background')
EMPTY = config['TILES'].getint('empty')
CORNER = config['TILES'].getint('corner')
THRONE = config['TILES'].getint('throne')
KING = config['TILES'].getint('king')
DEFENDER = config['TILES'].getint('defender')
ATTACKER = config['TILES'].getint('attacker')

# enum for current player
DEF = config['PLAYERS'].getint('defender')
ATK = config['PLAYERS'].getint('attacker')
DRAW = config['PLAYERS'].getint('defender')