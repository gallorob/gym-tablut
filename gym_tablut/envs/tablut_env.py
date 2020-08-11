import gym
from gym import spaces, logger
from gym.envs.classic_control import rendering
from gym.utils import seeding

from gym_tablut.envs._game_engine import *
from gym_tablut.envs._globals import *
from gym_tablut.envs._utils import *


class TablutEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 25
    }

    def __init__(self):
        """
        Create the environment
        """
        # environment variables
        self.action_space = spaces.Discrete(N_ROWS * N_COLS * N_ROWS * N_COLS)  # from(row, col) -> to(row, col)
        self.valid_actions = None
        self.observation_space = None
        self.done = False
        self.steps_beyond_done = None
        self.viewer = None
        # game variables
        self.board = np.zeros((N_ROWS, N_COLS))
        self.np_random = seeding.np_random(0)
        self.player = STARTING_PLAYER
        self.last_moves: List[Tuple[int, int, int, int]] = []
        self.n_moves = 0
        self.variant = 'tablut'
        self.game_engine = GameEngine(self.variant)

    def step(self, action: int) -> Tuple[np.ndarray, int, bool, dict]:
        """
        Apply a single step in the environment using the given action

        :param action: The action to apply
        """
        assert self.action_space.contains(action), f"[ERR: step] Unrecognized action: {action}"
        assert action in self.valid_actions, f"[ERR: step] Invalid action: {action}"

        info = {}
        if self.done:
            logger.warn('Stop calling `step()` after the episode is done! Use `reset()`')
            reward = 0
        else:
            move = decimal_to_space(action, self.board.shape[0], self.board.shape[1])
            res = self.game_engine.apply_move(self.board, move)
            move_str = res.get('move')
            reward = res.get('reward')
            logger.debug(f"[{str(self.n_moves + 1).zfill(int(np.log10(MAX_MOVES)) + 1)}/{MAX_MOVES}] "
                         f"{'ATK' if self.player == ATK else 'DEF'} : {move_str}")
            if res.get('game_over', False):
                self.done = True
                info = {
                    'winner': self.player,
                    'reason': 'King escaped' if self.player == DEF else 'King was captured',
                    'move': move_str
                }
            else:
                res = self.game_engine.check_endgame(last_moves=self.last_moves,
                                                     last_move=move,
                                                     player=self.player,
                                                     n_moves=self.n_moves)
                reward += res.get('reward')
                if res.get('game_over', False):
                    self.done = True
                    info = {
                        'winner': res.get('winner'),
                        'reason': res.get('reason'),
                        'move': move_str
                    }
                else:
                    # update moves short-term history
                    if len(self.last_moves) == 8:
                        self.last_moves.pop(0)
                    self.last_moves.append(move)

                    # update the action space
                    self.player = ATK if self.player == DEF else DEF
                    self.valid_actions = self.game_engine.legal_moves(self.board, self.player)

                    # no moves for the opponent check
                    if len(self.valid_actions) == 0:
                        self.done = True
                        reward += CAPTURE_REWARDS.get('king')
                        info = {
                            'winner': 'ATK' if self.player == DEF else 'DEF',
                            'reason': 'Opponents has no moves available',
                            'move': move_str
                        }
            if self.done:
                logger.debug(f"Match ended; reason: {info.get('reason')}; "
                             f"Winner: {'ATK' if info.get('winner') == ATK else ('DEF' if info.get('winner') == DEF else 'DRAW')}")
            self.n_moves += 1

        return self.board, reward, self.done, info

    def reset(self) -> np.array:
        """
        Reset the current scene, computing the observations

        :return: The state observations
        """
        self.done = False
        # place pieces
        self.board = np.zeros((N_ROWS, N_COLS))
        self.game_engine.fill_board(self.board)
        # initialize action space
        self.valid_actions = self.game_engine.legal_moves(self.board, STARTING_PLAYER)
        self.last_moves = []
        self.n_moves = 0
        logger.debug('New match started')
        return self.board

    def render(self, mode: str = 'human'):
        """
        Render the current state of the scene

        :param mode: The rendering mode to use
        """
        if self.viewer is None:
            self.viewer = rendering.Viewer(SCREEN_WIDTH, SCREEN_HEIGHT)

            # background
            tiles = make_background_geoms()
            for tile in tiles:
                self.viewer.add_geom(tile)
            # throne
            throne = rendering.Image(ASSETS.get(THRONE), SQUARE_WIDTH, SQUARE_HEIGHT)
            throne.set_color(1., 1., 1.)
            throne.add_attr(rendering.Transform(translation=((N_COLS // 2 + 1) * SQUARE_WIDTH + (SQUARE_WIDTH / 2),
                                                             (N_ROWS // 2 + 1) * SQUARE_HEIGHT + (SQUARE_HEIGHT / 2))))
            self.viewer.add_geom(throne)

        add_pieces_to_render(self.viewer, self.board)

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    def close(self):
        """
        Terminate the episode
        """
        if self.viewer:
            self.viewer.close()
            self.viewer = None


# -- Rendering aid functions --


def make_background_geoms():
    """
    Create the checkerboard background for the board
    """
    geoms = []
    # add the actual background
    background = rendering.Image(ASSETS.get(BACKGROUND), SCREEN_WIDTH, SCREEN_HEIGHT)
    background.set_color(1., 1., 1.)
    background.add_attr(rendering.Transform(translation=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
    geoms.append(background)
    # add the tiles
    c = 0
    for i in range(N_ROWS, 0, -1):
        for j in range(1, N_COLS + 1):
            tile = rendering.make_polygon([(i * SQUARE_WIDTH, j * SQUARE_HEIGHT),
                                           ((i + 1) * SQUARE_WIDTH, j * SQUARE_HEIGHT),
                                           ((i + 1) * SQUARE_WIDTH, (j + 1) * SQUARE_HEIGHT),
                                           (i * SQUARE_WIDTH, (j + 1) * SQUARE_HEIGHT)])
            r, g, b = BOARD_COLOR_0 if c == 0 else BOARD_COLOR_1
            tile.set_color(r, g, b)
            c = 1 if c == 0 else 0
            geoms.append(tile)
    return geoms


def add_pieces_to_render(viewer: rendering.Viewer, board: np.array):
    """
    Add the board's pieces to the renderer

    :param viewer: The renderer
    :param board: The board
    """
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            p = board[i, j]
            if p != EMPTY:
                r = i + 1
                c = j + 1
                tile = rendering.Image(ASSETS.get(p), SQUARE_WIDTH, SQUARE_HEIGHT)
                tile.set_color(1., 1., 1.)
                tile.add_attr(rendering.Transform(translation=(c * SQUARE_WIDTH + (SQUARE_WIDTH / 2),
                                                               (board.shape[0] - r + 1) * SQUARE_HEIGHT + (
                                                                           SQUARE_HEIGHT / 2))))
                viewer.add_onetime(tile)
