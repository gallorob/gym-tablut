from typing import Tuple, List

import numpy as np


DIRECTIONS = [(-1, 0),  # up
              (0, 1),  # right
              (1, 0),  # down
              (0, -1)  # left
              ]


def decimal_to_space(value: int, rows: int, cols: int) -> Tuple[int, int, int, int]:
    """
    Convert an integer to the 4D tuple `[rows - 1, cols - 1, rows - 1, cols - 1]`, checking that the value is positive
    and that `value < rows * cols * rows * cols`

    :param value: The integer to convert
    :param rows: The number of rows
    :param cols: The number of cols
    :return: The 4D tuple representation
    """
    assert value >= 0, f'[Conversion error]: Value is negative: {value}'
    assert value < rows * cols * rows * cols, f'[Conversion error]: Value {value} out of range in space [{rows}, ' \
                                              f'{cols}, {rows}, {cols}]'
    fi = value // (cols * rows * cols)
    r = value - (fi * cols * rows * cols)
    fj = r // (rows * cols)
    r -= fj * (rows * cols)
    ti = r // cols
    r -= ti * cols
    tj = r
    return fi, fj, ti, tj


def space_to_decimal(values: Tuple[int, int, int, int], rows: int, cols: int) -> int:
    """
    Convert a 4D tuple to its decimal representation, knowing that the space is defined as [rows, cols, rows, cols] with
    the maximum value being `[rows - 1, cols - 1, rows - 1, cols - 1]`

    :param values: The 4D tuple
    :param rows: The number of rows
    :param cols: The number of cols
    :return: The decimal representation
    """
    assert len(values) == 4, f'[Conversion error]: Unknown space value {values}'
    fi, fj, ti, tj = values
    assert fi < rows, f'[Conversion error]: From {values}: Invalid fi {fi} in [{rows}, {cols}, {rows}, {cols}]'
    assert fj < cols, f'[Conversion error]: From {values}: Invalid fj {fj} in [{rows}, {cols}, {rows}, {cols}]'
    assert ti < rows, f'[Conversion error]: From {values}: Invalid ti {ti} in [{rows}, {cols}, {rows}, {cols}]'
    assert tj < cols, f'[Conversion error]: From {values}: Invalid tj {tj} in [{rows}, {cols}, {rows}, {cols}]'
    return (fi * cols * rows * cols) + (fj * rows * cols) + (ti * cols) + tj


def vector_mask(vector: np.array, valid_indexes: np.array) -> np.array:
    """
    Create a mask vector with only the specified valid indexes set to 1, elsewhere to 0

    :param vector: The source vector
    :param valid_indexes: The list of valid indexes
    :return: A mask array with the same shape of vector
    """
    mask = np.zeros(vector.shape)
    for index in valid_indexes:
        assert index < len(vector), f'Invalid index {index} for vector with length {len(vector)}'
        mask[index] = 1
    return mask


def position_as_str(position: Tuple[int, int], rows: int) -> str:
    """
    Convert a position `(row, col)` to string

    :param position: The position
    :param rows: The number of rows in the board
    :return: The position as string
    """
    row = rows - position[0]
    col = chr(ord('a') + position[1])
    return col + str(row)


def position_as_tuple(position: str, rows: int) -> Tuple[int, int]:
    """
    Convert a position in string format to tuple `(row, col)`

    :param position: The position
    :param rows: The number of rows in the board
    :return: The position as tuple
    """
    row = rows - int(position[1])
    col = ord(position[0].lower()) - ord('a')
    return row, col


def on_edge_arr(board: np.array, position: Tuple[int, int]) -> bool:
    """
    Check if the array position is on the edge of the board

    :param board: The board
    :param position: The array position
    :return: True if it's an edge position, False otherwise
    """
    i, j = position
    return i == 0 or j == 0 or i == board.shape[0] - 1 or j == board.shape[1] - 1


def on_throne_arr(board: np.array, position: Tuple[int, int]) -> bool:
    """
    Check if the array position is the throne

    :param board: The board
    :param position: The array position
    :return: True if it's a throne position, False otherwise
    """
    i, j = position
    return i == board.shape[0] // 2 and j == board.shape[1] // 2


def next_to_throne_arr(board: np.array, position: Tuple[int, int]) -> bool:
    """
    Check if the array position is next to the throne

    :param board: The board
    :param position: The array position
    :return: True if the position is next to the throne, False otherwise
    """
    for (inc_i, inc_j) in DIRECTIONS:
        i, j = position
        if on_throne_arr(board, (i + inc_i, j + inc_j)):
            return True
    return False


def out_of_board_arr(board: np.array, position: Tuple[int, int]) -> bool:
    """
    Check if the array position is outside the board

    :param board: The board
    :param position: The position
    :return: True if it's outside the board, False otherwise
    """
    i, j = position
    return i < 0 or j < 0 or i >= board.shape[0] or j >= board.shape[1]


# Current State has to have the same From/To as the one four moves before (-4) and the same To as the one eight
# moves prior (-8). The -1 move has to have the same from/to as the -5, the -2 as the -6 and the -3 as the -7
def check_threefold_repetition(last_moves: List[Tuple[int, int, int, int]], last_move: Tuple[int, int, int, int]):
    """
    Check for the threefold repetition rule.
    From Fellhuhn's Hnefatafl app: the last move has to be the same as the one four moves (-4) before and with the same
    destination tile as the one eight moves prior (-8). The (-1) move has to be the same as the (-5), the (-2) as the
    (-6) and the (-3) as the (-7)
    :param last_moves: The last move that have been played
    :param last_move: A queue with the latest moves
    :return: True if the threefold repetition rule is satisfied, False otherwise
    """
    if len(last_moves) < 8:
        return False
    else:
        return ((last_move == last_moves[4]) and
                (last_move[3:] == last_moves[0][3:]) and
                last_moves[7] == last_moves[3] and
                last_moves[6] == last_moves[2] and
                last_moves[5] == last_moves[1])
