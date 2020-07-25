import gym
from gym import spaces, logger
from gym.utils import seeding

from gym_tablut.envs._game_engine import *


class TablutEnv(gym.Env):
    def __init__(self):
        """
        Create the environment
        """
        self.action_space = None
        self.actions = None
        self.observation_space = None
        self.board = Board(N_ROWS, N_COLS)
        self.done = False
        self.steps_beyond_done = None
        self.viewer = None
        self.np_random = seeding.np_random(0)

    def step(self, action: int, player: int) -> Tuple[np.ndarray, int, bool, dict]:
        """
        Apply a single step in the environment using the given action

        :param action: The action to apply
        :param player: The playing actor
        """
        assert player in [ATK, DEF], "[ERR: step] Unrecognized player type: {}".format(player)
        assert self.action_space.contains(action), "[ERR: step] Unrecognized action: {}".format(action)

        info = {}

        if self.done:
            logger.warn('Stop calling `step()` after the episode is done! Use `reset()`')
            rewards = 0
        else:
            logger.debug('{} moved {}'.format('Attacker' if player == ATK else 'Defender', self.actions[action]))

            move = split_move(self.actions[action])
            rewards, captured = apply_move(self.board, move)

            # remove captured piece from render
            for p in captured:
                self.viewer.geoms.remove(p.texture)

            # check if game is over
            self.done = self.board.king_escaped or not self.board.king_alive
            if self.done:
                info['reason'] = 'King has escaped' if self.board.king_escaped else 'King was captured'
                info['last_move'] = self.actions[action]
                info['n_atks'] = self.board.count(ATTACKER)
                info['n_defs'] = self.board.count(DEFENDER)

            # update the action space
            next_player = ATK if player == DEF else DEF
            self.actions = legal_moves(self.board, next_player)
            self.action_space = spaces.Discrete(len(self.actions))

            if len(self.actions) == 0:
                self.done = True
                rewards = CAPTURE_REWARDS.get('king')
                info['reason'] = 'No more moves available'
                info['last_move'] = self.actions[action]
                info['n_atks'] = self.board.count(ATTACKER)
                info['n_defs'] = self.board.count(DEFENDER)

        # return observations, reward, done, infos
        return self.board.state, rewards, self.done, info

    def reset(self):
        """
        Reset the current scene, computing the observations

        :return: The state observations
        """
        if self.viewer:
            remove_pieces_from_render(self.viewer, self.board)
        self.done = False
        # place pieces
        self.board.reset()
        fill_board(self.board)
        if self.viewer:
            add_pieces_to_render(self.viewer, self.board)
        # initialize action space
        self.actions = legal_moves(self.board, STARTING_PLAYER)
        self.action_space = spaces.Discrete(len(self.actions))
        return self.board.state

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
            throne = rendering.Image(ASSETS.get('throne'), SQUARE_WIDTH, SQUARE_HEIGHT)
            throne.set_color(1., 1., 1.)
            throne.add_attr(rendering.Transform(translation=((N_COLS // 2 + 1) * SQUARE_WIDTH + (SQUARE_WIDTH / 2),
                                                             (N_ROWS // 2 + 1) * SQUARE_HEIGHT + (SQUARE_HEIGHT / 2))))
            self.viewer.add_geom(throne)
            # references
            refs = make_reference_geoms()
            for ref in refs:
                self.viewer.add_geom(ref)
            # pieces
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


def make_reference_geoms():
    """
    Create the row numbers and column letters to display next to the board
    """
    geoms = []
    # add the row numbers from 9 to 1
    for i in range(N_ROWS, 0, -1):
        img = rendering.Image(ASSETS.get('rows').get(i - 1), SQUARE_WIDTH, SQUARE_HEIGHT)
        img.set_color(1., 1., 1.)
        img.add_attr(rendering.Transform(translation=(SQUARE_WIDTH / 2, i * SQUARE_HEIGHT + (SQUARE_HEIGHT / 2))))
        geoms.append(img)
    # add the column letters from a to i
    for j in range(1, N_COLS + 1):
        img = rendering.Image(ASSETS.get('columns').get(j - 1), SQUARE_WIDTH, SQUARE_HEIGHT)
        img.set_color(1., 1., 1.)
        img.add_attr(rendering.Transform(translation=(j * SQUARE_WIDTH + (SQUARE_WIDTH / 2), SQUARE_HEIGHT / 2)))
        geoms.append(img)
    return geoms


def add_pieces_to_render(viewer: rendering.Viewer, board: Board):
    """
    Add the board's pieces to the renderer

    :param viewer: The renderer
    :param board: The board
    """
    for i in range(board.rows):
        for j in range(board.cols):
            p = board.state[i, j]
            if p is not None:
                r, c = pos_to_arr(board, p.position)
                r += 1
                c += 1
                p.trans.set_translation(c * SQUARE_WIDTH + (SQUARE_WIDTH / 2),
                                        (board.rows - r + 1) * SQUARE_HEIGHT + (SQUARE_HEIGHT / 2))
                viewer.add_geom(p.texture)


def remove_pieces_from_render(viewer, board):
    """
    Remove the board's pieces from the renderer

    :param viewer: The renderer
    :param board: The board
    """
    for i in range(board.rows):
        for j in range(board.cols):
            p = board.state[i][j]
            if p is not None:
                viewer.geoms.remove(p.texture)
