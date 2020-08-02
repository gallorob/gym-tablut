import os

# location independent assets directory
assets_dir = os.path.dirname(__file__)
assets_dir = os.path.join(assets_dir, 'assets')

# game & rendering variables
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
N_ROWS = 9
N_COLS = 9
MAX_MOVES = 300
SQUARE_WIDTH = SCREEN_WIDTH / (N_COLS + 1)
SQUARE_HEIGHT = SCREEN_HEIGHT / (N_ROWS + 1)
BOARD_COLOR_0 = [0.5, 0.33, 0.16]
BOARD_COLOR_1 = [0.4, 0.26, 0.13]

# assets for tiles and background
ASSETS = {
    'defender': os.path.join(assets_dir, 'defender.png'),
    'attacker': os.path.join(assets_dir, 'attacker.png'),
    'king': os.path.join(assets_dir, 'king.png'),
    'throne': os.path.join(assets_dir, 'throne.png'),
    'background': os.path.join(assets_dir, 'background.png')
}

# enum for current player
DEF = 0
ATK = 1
STARTING_PLAYER = ATK

# dictionary variables
ATTACKER = 'attacker'
DEFENDER = 'defender'
KING = 'king'

# rewards
CAPTURE_REWARDS = {
    ATTACKER: 1,
    DEFENDER: 2,
    KING: 16
}
DRAW_REWARD = 0

# state representation
RENDER_STATE = True  # this is the default value, can be changed in the env
STATE_REP = {
    ATTACKER: {
        True: [1., 0., 0.],
        False: 1
    },
    DEFENDER: {
        True: [0., 0., 1.],
        False: 2
    },
    KING: {
        True: [0., 1., 0.],
        False: 3
    }
}
