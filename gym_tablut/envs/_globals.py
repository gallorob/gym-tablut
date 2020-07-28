import os

assets_dir = os.path.dirname(__file__)
assets_dir = os.path.join(assets_dir, 'assets')

rows_dir = os.path.join(assets_dir, 'rows')
columns_dir = os.path.join(assets_dir, 'columns')

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
N_ROWS = 9
N_COLS = 9
SQUARE_WIDTH = SCREEN_WIDTH / (N_COLS + 1)
SQUARE_HEIGHT = SCREEN_HEIGHT / (N_ROWS + 1)

BOARD_COLOR_0 = [0.5, 0.33, 0.16]
BOARD_COLOR_1 = [0.4, 0.26, 0.13]

ASSETS = {
    'defender': os.path.join(assets_dir, 'defender.png'),
    'attacker': os.path.join(assets_dir, 'attacker.png'),
    'king':     os.path.join(assets_dir, 'king.png'),
    'throne':   os.path.join(assets_dir, 'throne.png'),
    'columns': {
        0: os.path.join(columns_dir, '1.png'),
        1: os.path.join(columns_dir, '2.png'),
        2: os.path.join(columns_dir, '3.png'),
        3: os.path.join(columns_dir, '4.png'),
        4: os.path.join(columns_dir, '5.png'),
        5: os.path.join(columns_dir, '6.png'),
        6: os.path.join(columns_dir, '7.png'),
        7: os.path.join(columns_dir, '8.png'),
        8: os.path.join(columns_dir, '9.png')
    },
    'rows': {
        0: os.path.join(rows_dir, '1.png'),
        1: os.path.join(rows_dir, '2.png'),
        2: os.path.join(rows_dir, '3.png'),
        3: os.path.join(rows_dir, '4.png'),
        4: os.path.join(rows_dir, '5.png'),
        5: os.path.join(rows_dir, '6.png'),
        6: os.path.join(rows_dir, '7.png'),
        7: os.path.join(rows_dir, '8.png'),
        8: os.path.join(rows_dir, '9.png')
    }
}

DEF = 0
ATK = 1

ATTACKER = 'attacker'
DEFENDER = 'defender'
KING = 'king'

STARTING_PLAYER = ATK

CAPTURE_REWARDS = {
    ATTACKER: 1,
    DEFENDER: 2,
    KING: 16
}
DRAW_REWARD = 0

RENDER_STATE = True

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
