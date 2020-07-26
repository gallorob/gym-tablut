SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
N_ROWS = 9
N_COLS = 9
SQUARE_WIDTH = SCREEN_WIDTH / (N_COLS + 1)
SQUARE_HEIGHT = SCREEN_HEIGHT / (N_ROWS + 1)

BOARD_COLOR_0 = [0.5, 0.33, 0.16]
BOARD_COLOR_1 = [0.4, 0.26, 0.13]

ASSETS = {
    'defender': 'gym_tablut/envs/assets/defender.png',
    'attacker': 'gym_tablut/envs/assets/attacker.png',
    'king':     'gym_tablut/envs/assets/king.png',
    'throne':   'gym_tablut/envs/assets/throne.png',
    'columns': {
        0: 'gym_tablut/envs/assets/columns/1.png',
        1: 'gym_tablut/envs/assets/columns/2.png',
        2: 'gym_tablut/envs/assets/columns/3.png',
        3: 'gym_tablut/envs/assets/columns/4.png',
        4: 'gym_tablut/envs/assets/columns/5.png',
        5: 'gym_tablut/envs/assets/columns/6.png',
        6: 'gym_tablut/envs/assets/columns/7.png',
        7: 'gym_tablut/envs/assets/columns/8.png',
        8: 'gym_tablut/envs/assets/columns/9.png'
    },
    'rows': {
        0: 'gym_tablut/envs/assets/rows/1.png',
        1: 'gym_tablut/envs/assets/rows/2.png',
        2: 'gym_tablut/envs/assets/rows/3.png',
        3: 'gym_tablut/envs/assets/rows/4.png',
        4: 'gym_tablut/envs/assets/rows/5.png',
        5: 'gym_tablut/envs/assets/rows/6.png',
        6: 'gym_tablut/envs/assets/rows/7.png',
        7: 'gym_tablut/envs/assets/rows/8.png',
        8: 'gym_tablut/envs/assets/rows/9.png',
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
