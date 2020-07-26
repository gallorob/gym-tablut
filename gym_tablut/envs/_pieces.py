from typing import Tuple

import numpy as np
from gym.envs.classic_control import rendering

from gym_tablut.envs._globals import *


class Piece:
    def __init__(self, _type: str, position: Tuple[str, int]):
        """
        Create a piece

        :param _type: The piece's type
        :param position: The piece's position on the board
        """
        self.type = _type
        self.position = position
        self.picture = ASSETS.get(self.type)
        self.trans = rendering.Transform()
        self.texture = self.make_texture()

    def make_texture(self):
        """
        Create the render image to render on the board
        """
        img = rendering.Image(self.picture, SQUARE_WIDTH, SQUARE_HEIGHT)
        img.set_color(1., 1., 1.)
        img.add_attr(self.trans)
        return img


class Defender(Piece):
    def __init__(self, position: Tuple[str, int]):
        """
        Create a defender piece

        :param position: The piece's position on the board
        """
        super().__init__(_type=DEFENDER,
                         position=position)


class Attacker(Piece):
    def __init__(self, position: Tuple[str, int]):
        """
        Create an attacker piece

        :param position: The piece's position on the board
        """
        super().__init__(_type=ATTACKER,
                         position=position)


class King(Piece):
    def __init__(self, position: Tuple[str, int]):
        """
        Create a king piece

        :param position: The piece's position on the board
        """
        super().__init__(_type=KING,
                         position=position)


class Board:
    def __init__(self, n_rows: int, n_cols: int):
        """
        Create a board

        :param n_rows: The number of rows (ranks)
        :param n_cols: The number of columns (files)
        """
        self.rows = n_rows
        self.cols = n_cols
        self.state = np.empty((n_rows, n_cols), dtype=Piece)
        self.king_alive = True
        self.king_escaped = False

    def reset(self):
        """
        Reset the board state
        """
        self.state = np.empty((self.rows, self.cols), dtype=Piece)
        self.king_alive = True
        self.king_escaped = False

    def count(self, _type: str) -> int:
        """
        Count how many pieces of type `_type` are on the board
        :param _type: The type
        :return: The number of pieces of the desired type
        """
        c = 0
        for i in range(self.rows):
            for j in range(self.cols):
                p = self.state[i][j]
                if p is not None:
                    c += 1 if p.type == _type else 0
        return c

    def as_state(self, render_state: bool = False) -> np.ndarray:
        """
        Convert the board to an observation state.

        The result is either a matrix of values or a RGB matrix.

        :param render_state: If True, converts to a RGB matrix
        :return: A matrix of values
        """
        shape = (self.rows, self.cols, 3) if render_state else (self.rows, self.cols)
        state = np.zeros(shape)
        # fill matrix
        for i in range(self.rows):
            for j in range(self.cols):
                p = self.state[i][j]
                if p is not None:
                    state[i, j] = STATE_REP.get(p.type).get(render_state)
        # return
        return state
