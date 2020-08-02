import gym
from gym import spaces, logger
from gym.utils import seeding

from gym_tablut.envs._game_engine import *


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
        self.action_space = None
        self.actions = None
        self.observation_space = None
        self.done = False
        self.steps_beyond_done = None
        self.viewer = None
        # game variables
        self.board = Board(N_ROWS, N_COLS)
        self.np_random = seeding.np_random(0)
        self.player = STARTING_PLAYER
        self.rgb_state = RENDER_STATE
        self.last_moves = []
        self.n_moves = 0

    def step(self, action: int) -> Tuple[np.ndarray, int, bool, dict]:
        """
        Apply a single step in the environment using the given action

        :param action: The action to apply
        """
        assert self.action_space.contains(action), f"[ERR: step] Unrecognized action: {action}"

        info = {'captured': []}

        if self.done:
            logger.warn('Stop calling `step()` after the episode is done! Use `reset()`')
            rewards = 0
        else:
            logger.debug(f"{'Attacker' if self.player == ATK else 'Defender'} moved {self.actions[action]}")

            move = split_move(self.actions[action])
            rewards, captured = apply_move(self.board, move)

            if len(captured) > 0:
                s = []
                # remove captured piece from render
                for p in captured:
                    info.get('captured').append(str_position(p.position))
                    s.append(f"{p.type} in {str_position(p.position)}")
                    if self.viewer:
                        self.viewer.geoms.remove(p.texture)
                logger.debug(f"Captured {len(captured)} piece(s): {';'.join(s)}")

            # check if game is over
            self.done = self.board.king_escaped or not self.board.king_alive
            if self.done:
                reason = 'King has escaped' if self.board.king_escaped else 'King was captured'
                info['winner'] = 'DEF' if self.board.king_escaped else 'ATK'
                info['reason'] = reason
                info['last_move'] = self.actions[action]
                info['n_atks'] = self.board.count(ATTACKER)
                info['n_defs'] = self.board.count(DEFENDER)
                logger.debug(f"Match ended; reason: {reason}; Winner: {info.get('winner')}")
            # threefold repetition check
            if check_threefold_repetition(self.last_moves, self.actions[action]):
                logger.debug(
                    f"Match ended; reason: Threefold repetition; DRAW")
                self.done = True
                rewards = DRAW_REWARD
                info['reason'] = 'Threefold repetition'
                info['last_move'] = self.actions[action]
                info['n_atks'] = self.board.count(ATTACKER)
                info['n_defs'] = self.board.count(DEFENDER)
            else:
                if len(self.last_moves) == 8:
                    self.last_moves.pop()
                self.last_moves.append(self.actions[action])
            # max moves reached
            if self.n_moves == MAX_MOVES:
                self.done = True
                rewards = 0
                info['reason'] = 'Maximum number of moves reached'
                info['last_move'] = self.actions[action]
                info['n_atks'] = self.board.count(ATTACKER)
                info['n_defs'] = self.board.count(DEFENDER)

            # update the action space
            self.player = ATK if self.player == DEF else DEF
            self.actions = legal_moves(self.board, self.player)
            self.action_space = spaces.Discrete(len(self.actions))

            # no moves for the opponent check
            if len(self.actions) == 0:
                self.done = True
                rewards = CAPTURE_REWARDS.get('king')
                info['winner'] = 'ATK' if self.player == DEF else 'DEF'
                info['reason'] = 'No more moves available'
                info['last_move'] = self.actions[action]
                info['n_atks'] = self.board.count(ATTACKER)
                info['n_defs'] = self.board.count(DEFENDER)
                logger.debug(
                    f"Match ended; reason: No more moves available; Winner: {info.get('winner')}")
        self.n_moves += 1
        obs = self.board.as_state(self.rgb_state)

        return obs, rewards, self.done, info

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
        self.last_moves = []
        self.n_moves = 0
        logger.debug('New match started')
        return self.board.as_state(self.rgb_state)

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
    # add the actual background
    background = rendering.Image(ASSETS.get('background'), SCREEN_WIDTH, SCREEN_HEIGHT)
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


def remove_pieces_from_render(viewer: rendering.Viewer, board: Board):
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
