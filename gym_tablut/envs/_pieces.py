from typing import Tuple, List
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
        self._type = _type
        self.position = position
        self.picture = ASSETS.get(self._type)
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
        super().__init__(_type='defender',
                         position=position)


class Attacker(Piece):
    def __init__(self, position: Tuple[str, int]):
        """
        Create an attacker piece

        :param position: The piece's position on the board
        """
        super().__init__(_type='attacker',
                         position=position)


class King(Piece):
    def __init__(self, position: Tuple[str, int]):
        """
        Create a king piece

        :param position: The piece's position on the board
        """
        super().__init__(_type='king',
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

    def fill_board(self):
        """
        Populate the board. By default, uses the standard Tablut configuration
        """
        # add king
        self.state[4][4] = King(self.arr_to_pos((4, 4)))
        # add defenders
        self.state[2][4] = Defender(self.arr_to_pos((2, 4)))
        self.state[3][4] = Defender(self.arr_to_pos((3, 4)))
        self.state[4][2] = Defender(self.arr_to_pos((4, 2)))
        self.state[4][3] = Defender(self.arr_to_pos((4, 3)))
        self.state[4][5] = Defender(self.arr_to_pos((4, 5)))
        self.state[4][6] = Defender(self.arr_to_pos((4, 6)))
        self.state[5][4] = Defender(self.arr_to_pos((5, 4)))
        self.state[6][4] = Defender(self.arr_to_pos((6, 4)))
        # add attackers
        self.state[0][3] = Attacker(self.arr_to_pos((0, 3)))
        self.state[0][4] = Attacker(self.arr_to_pos((0, 4)))
        self.state[0][5] = Attacker(self.arr_to_pos((0, 5)))
        self.state[1][4] = Attacker(self.arr_to_pos((1, 4)))
        self.state[3][0] = Attacker(self.arr_to_pos((3, 0)))
        self.state[3][8] = Attacker(self.arr_to_pos((3, 8)))
        self.state[4][0] = Attacker(self.arr_to_pos((4, 0)))
        self.state[4][1] = Attacker(self.arr_to_pos((4, 1)))
        self.state[4][7] = Attacker(self.arr_to_pos((4, 7)))
        self.state[4][8] = Attacker(self.arr_to_pos((4, 8)))
        self.state[5][0] = Attacker(self.arr_to_pos((5, 0)))
        self.state[5][8] = Attacker(self.arr_to_pos((5, 8)))
        self.state[7][4] = Attacker(self.arr_to_pos((7, 4)))
        self.state[8][3] = Attacker(self.arr_to_pos((8, 3)))
        self.state[8][4] = Attacker(self.arr_to_pos((8, 4)))
        self.state[8][5] = Attacker(self.arr_to_pos((8, 5)))

    def arr_to_pos(self, arr: Tuple[int, int]) -> Tuple[str, int]:
        """
        Convert array indexes to board position

        :param arr: The indexes for the array
        :return: The board position as (file, rank)
        """
        col = chr(ord('a') + arr[1])
        row = self.rows - arr[0]
        return col, row

    def pos_to_arr(self, pos: Tuple[str, int]) -> Tuple[int, int]:
        """
        Convert the board position to array indexes

        :param pos: The board position
        :return: The array indexes as (j, i)
        """
        col = ord(pos[0].lower()) - ord('a')
        row = self.rows - pos[1]
        return row, col

    def update_piece_position(self, piece: Piece, pos: Tuple[str, int]):
        """
        Update a piece's position and its transform matrix

        :param piece: The piece to update
        :param pos: The new position
        """
        piece.position = pos
        i, j = self.pos_to_arr(pos)
        i += 1
        j += 1
        piece.trans.set_translation(i * SQUARE_WIDTH + (SQUARE_WIDTH / 2),
                                    j * SQUARE_HEIGHT + (SQUARE_HEIGHT / 2))


def legal_moves(board: Board, player: int) -> np.ndarray:
    """
    Compute the legal and valid moves for the player in a given board configuration

    :param board: The current board
    :param player: The player (either ATTACKER or DEFENDER)
    :return: A numpy array of moves in string format `from`-`to`
    """
    assert player in [ATTACKER, DEFENDER], "[ERR: legal_moves] Unrecognized player type: {}".format(player)
    moves = []
    for i in range(board.rows):
        for j in range(board.cols):
            p = board.state[i][j]
            if p is not None:
                if p._type == 'attacker' and player == ATTACKER:
                    moves.extend(_legal_moves(board, p))
                elif p._type != 'attacker' and player == DEFENDER:
                    moves.extend(_legal_moves(board, p))
    return np.array(moves)


def _legal_moves(board: Board, piece: Piece) -> List[str]:
    """
    Compute the legal and valid moves for the selected piece in the given board

    :param board: The current board
    :param piece: The selected piece
    :return: A list of valid moves for the piece in the given board
    """
    moves = []
    moves.extend(__legal_moves(board, piece, 0, -1))  # right
    moves.extend(__legal_moves(board, piece, 1, 0))   # down
    moves.extend(__legal_moves(board, piece, 0, 1))   # left
    moves.extend(__legal_moves(board, piece, -1, 0))  # up
    return moves


def __legal_moves(board: Board, piece: Piece, inc_row: int, inc_col: int) -> List[str]:
    """
    Compute the legal and valid moves for the selected in the given board along the selected axis

    :param board: The current board
    :param piece: The selected piece
    :param inc_row: Trajectory: 1 for down, -1 for up, 0 for no change
    :param inc_col: Trajectory: 1 for left, -1 for right, 0 for no change
    :return: A list of valid moves for the piece in the given board along the selected axis
    """
    moves = []
    (i, j) = board.pos_to_arr(piece.position)
    while True:
        i += inc_row
        j += inc_col
        if i < 0 or i > board.rows - 1 or j < 0 or j > board.cols - 1:
            break
        p = board.state[i][j]
        if p is None:
            (ni, nj) = board.arr_to_pos((i, j))
            moves.append(str_position(piece.position) + '-' + str_position((ni, nj)))
        else:
            break
    return moves


def str_position(pos: Tuple[str, int]) -> str:
    """
    Transform a board position in a single string

    :param pos: The board position
    :return: A string representation of the position
    """
    return pos[0] + str(pos[1])
