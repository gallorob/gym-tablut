import os

N_ROWS = 9
N_COLS = 9

# location independent assets directory
assets_dir = os.path.dirname(__file__)
assets_dir = os.path.join(assets_dir, 'assets')

# game & rendering variables
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
MAX_MOVES = 300
SQUARE_WIDTH = SCREEN_WIDTH / (N_COLS + 1)
SQUARE_HEIGHT = SCREEN_HEIGHT / (N_ROWS + 1)
BOARD_COLOR_0 = [0.5, 0.33, 0.16]
BOARD_COLOR_1 = [0.4, 0.26, 0.13]

# tile values
BACKGROUND = -1
EMPTY = 0
CORNER = 1
THRONE = 2
KING = 3
DEFENDER = 4
ATTACKER = 5

# assets for tiles and background
ASSETS = {
    DEFENDER: os.path.join(assets_dir, 'defender.png'),
    ATTACKER: os.path.join(assets_dir, 'attacker.png'),
    KING: os.path.join(assets_dir, 'king.png'),
    THRONE: os.path.join(assets_dir, 'throne.png'),
    CORNER: os.path.join(assets_dir, 'throne.png'),
    BACKGROUND: os.path.join(assets_dir, 'background.png')
}

# enum for current player
DEF = 0
ATK = 1
STARTING_PLAYER = ATK
DRAW = -1

# rewards
CAPTURE_REWARDS = {
    ATTACKER: 1,
    DEFENDER: 2,
    KING: 16
}
DRAW_REWARD = 0

# utils
DIRECTIONS = [(-1, 0),  # up
              (0, 1),  # right
              (1, 0),  # down
              (0, -1)  # left
              ]
