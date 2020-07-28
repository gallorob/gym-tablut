from gym_tablut.envs._pieces import *


def arr_to_pos(board: Board, arr: Tuple[int, int]) -> Tuple[str, int]:
    """
    Convert array indexes to board position

    :param board: The board
    :param arr: The indexes for the array
    :return: The board position as (file, rank)
    """
    col = chr(ord('a') + arr[1])
    row = board.rows - arr[0]
    return col, row


def pos_to_arr(board: Board, pos: Tuple[str, int]) -> Tuple[int, int]:
    """
    Convert the board position to array indexes

    :param board: The board
    :param pos: The board position
    :return: The array indexes as (i, j)
    """
    col = ord(pos[0].lower()) - ord('a')
    row = board.rows - pos[1]
    return row, col


def on_edge_pos(board: Board, position: Tuple[str, int]) -> bool:
    """
    Check if the position is on the edge of the board

    :param board: The board
    :param position: The position
    :return: True if it's an edge position, False otherwise
    """
    i, j = pos_to_arr(board, position)
    return on_edge_arr(board, (i, j))


def on_edge_arr(board: Board, position: Tuple[int, int]) -> bool:
    """
    Check if the array position is on the edge of the board

    :param board: The board
    :param position: The array position
    :return: True if it's an edge position, False otherwise
    """
    i, j = position
    return i == 0 or j == 0 or i == board.rows - 1 or j == board.cols - 1


def on_throne_pos(board: Board, position: Tuple[str, int]) -> bool:
    """
    Check if the position is the throne

    :param board:  The board
    :param position: The position
    :return: True if it's a throne position, False otherwise
    """
    i, j = pos_to_arr(board, position)
    return on_throne_arr(board, (i, j))


def on_throne_arr(board: Board, position: Tuple[int, int]) -> bool:
    """
    Check if the array position is the throne

    :param board: The board
    :param position: The array position
    :return: True if it's a throne position, False otherwise
    """
    i, j = position
    return i == board.rows // 2 and j == board.cols // 2


def next_to_throne_arr(board: Board, position: Tuple[int, int]) -> bool:
    """
    Check if the array position is next to the throne

    :param board: The board
    :param position: The array position
    :return: True if the position is next to the throne, False otherwise
    """
    return _next_to_throne_arr(board, position, -1, 0) or \
           _next_to_throne_arr(board, position, 0, 1) or \
           _next_to_throne_arr(board, position, 1, 0) or \
           _next_to_throne_arr(board, position, 0, -1)


def _next_to_throne_arr(board: Board, position: Tuple[int, int], row_inc: int, col_inc: int) -> bool:
    """
    Check if the position is next to the throne in the given trajectory

    :param board: The board
    :param position: The array position
    :param row_inc: Trajectory: 1 for down, -1 for up, 0 for no change
    :param col_inc: Trajectory: 1 for left, -1 for right, 0 for no change
    :return: True if the position is next to the throne, False otherwise
    """
    (i, j) = position
    i += row_inc
    j += col_inc
    return on_throne_arr(board, (i, j))


def out_of_board_pos(board, position: Tuple[str, int]) -> bool:
    """
    Check if the position is outside the board

    :param board: The board
    :param position: The position
    :return: True if it's outside the board, False otherwise
    """
    i, j = board.pos_to_arr(position)
    return out_of_board_arr(board, (i, j))


def out_of_board_arr(board: Board, position: Tuple[int, int]) -> bool:
    """
    Check if the array position is outside the board

    :param board: The board
    :param position: The position
    :return: True if it's outside the board, False otherwise
    """
    i, j = position
    return i < 0 or j < 0 or i >= board.rows or j >= board.cols


def str_position(pos: Tuple[str, int]) -> str:
    """
    Transform a board position in a single string

    :param pos: The board position
    :return: A string representation of the position
    """
    return pos[0] + str(pos[1])


def split_move(move: str) -> Tuple[Tuple[str, int], Tuple[str, int]]:
    """
    Create a move (`from_pos`, `to_pos`) from the string `from_str-to_str`

    :param move: The move in string format
    :return: The move as tuples
    """
    assert len(move) == 5, '[ERR: split_move]: Unrecognized move format: {}'.format(move)
    p_from = (move[0], int(move[1]))
    p_to = (move[3], int(move[4]))
    return p_from, p_to


# Current State has to have the same From/To as the one four moves before (-4) and the same To as the one eight
# moves prior (-8). The -1 move has to have the same from/to as the -5, the -2 as the -6 and the -3 as the -7
def check_threefold_repetition(last_moves, last_move):
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
                (str_position(split_move(last_move)[1]) == str_position(split_move(last_moves[0])[1])) and
                last_moves[7] == last_moves[3] and
                last_moves[6] == last_moves[2] and
                last_moves[5] == last_moves[1])


def fill_board(board: Board):
    """
    Populate the board. By default, uses the standard Tablut configuration
    """
    # add king
    board.state[4, 4] = King(arr_to_pos(board, (4, 4)))
    # add defenders
    board.state[2, 4] = Defender(arr_to_pos(board, (2, 4)))
    board.state[3, 4] = Defender(arr_to_pos(board, (3, 4)))
    board.state[4, 2] = Defender(arr_to_pos(board, (4, 2)))
    board.state[4, 3] = Defender(arr_to_pos(board, (4, 3)))
    board.state[4, 5] = Defender(arr_to_pos(board, (4, 5)))
    board.state[4, 6] = Defender(arr_to_pos(board, (4, 6)))
    board.state[5, 4] = Defender(arr_to_pos(board, (5, 4)))
    board.state[6, 4] = Defender(arr_to_pos(board, (6, 4)))
    # add attackers
    board.state[0, 3] = Attacker(arr_to_pos(board, (0, 3)))
    board.state[0, 4] = Attacker(arr_to_pos(board, (0, 4)))
    board.state[0, 5] = Attacker(arr_to_pos(board, (0, 5)))
    board.state[1, 4] = Attacker(arr_to_pos(board, (1, 4)))
    board.state[3, 0] = Attacker(arr_to_pos(board, (3, 0)))
    board.state[3, 8] = Attacker(arr_to_pos(board, (3, 8)))
    board.state[4, 0] = Attacker(arr_to_pos(board, (4, 0)))
    board.state[4, 1] = Attacker(arr_to_pos(board, (4, 1)))
    board.state[4, 7] = Attacker(arr_to_pos(board, (4, 7)))
    board.state[4, 8] = Attacker(arr_to_pos(board, (4, 8)))
    board.state[5, 0] = Attacker(arr_to_pos(board, (5, 0)))
    board.state[5, 8] = Attacker(arr_to_pos(board, (5, 8)))
    board.state[7, 4] = Attacker(arr_to_pos(board, (7, 4)))
    board.state[8, 3] = Attacker(arr_to_pos(board, (8, 3)))
    board.state[8, 4] = Attacker(arr_to_pos(board, (8, 4)))
    board.state[8, 5] = Attacker(arr_to_pos(board, (8, 5)))
