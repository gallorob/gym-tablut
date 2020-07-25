from typing import List

from gym_tablut.envs._utils import *


def update_piece_position(board: Board, piece: Piece, pos: Tuple[str, int]):
    """
    Update a piece's position and its transform matrix

    :param board: The board
    :param piece: The piece to update
    :param pos: The new position
    """
    piece.position = pos
    i, j = pos_to_arr(board, pos)
    i += 1
    j += 1
    piece.trans.set_translation(j * SQUARE_WIDTH + (SQUARE_WIDTH / 2),
                                (board.rows - i + 1) * SQUARE_HEIGHT + (SQUARE_HEIGHT / 2))


def apply_move(board: Board, move: Tuple[Tuple[str, int], Tuple[str, int]]) -> Tuple[int, List[Piece]]:
    """
    Apply the move, processing also captures

    :param board: The board
    :param move: The move
    :return: The reward and the list of captured pieces
    """
    p_from, p_to = move
    # check moved piece
    i_f, j_f = pos_to_arr(board, p_from)
    moved_piece = board.state[i_f, j_f]
    assert moved_piece is not None, "[ERR: apply_move] Moved piece is None"
    # check destination tile
    i_t, j_t = pos_to_arr(board, p_to)
    dest_tile = board.state[i_t, j_t]
    assert dest_tile is None, "[Err: apply_move] Destination tile is not empty"
    # update board and piece
    board.state[i_f, j_f] = None
    board.state[i_t, j_t] = moved_piece
    update_piece_position(board, moved_piece, p_to)
    # king can't capture but can escape
    if moved_piece.type == KING:
        board.king_escaped = on_edge_pos(board, moved_piece.position)
        return CAPTURE_REWARDS.get(KING) if board.king_escaped else 0, []
    else:
        to_remove = process_captures(board, moved_piece)
        reward = 0
        for p in to_remove:
            i, j = pos_to_arr(board, p.position)
            board.state[i, j] = None
            reward += CAPTURE_REWARDS.get(p.type)
            # check if it was the king
            if p.type == KING:
                board.king_alive = False
        return reward, to_remove


def legal_moves(board: Board, player: int) -> np.ndarray:
    """
    Compute the legal and valid moves for the player in a given board configuration

    :param board: The current board
    :param player: The player (either ATTACKER or DEFENDER)
    :return: A numpy array of moves in string format `from`-`to`
    """
    assert player in [ATK, DEF], "[ERR: legal_moves] Unrecognized player type: {}".format(player)
    moves = []
    for i in range(board.rows):
        for j in range(board.cols):
            p = board.state[i][j]
            if p is not None:
                if p.type == ATTACKER and player == ATK:
                    moves.extend(_legal_moves(board, p))
                elif p.type != ATTACKER and player == DEF:
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
    moves.extend(__legal_moves(board, piece, 0, -1))  # left
    moves.extend(__legal_moves(board, piece, 1, 0))  # down
    moves.extend(__legal_moves(board, piece, 0, 1))  # right
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
    (i, j) = pos_to_arr(board, piece.position)
    while True:
        i += inc_row
        j += inc_col
        if i < 0 or i > board.rows - 1 or j < 0 or j > board.cols - 1:
            break
        p = board.state[i][j]
        if p is None:
            # only king can cross or land on throne
            if piece.type != KING and i == board.rows // 2 and j == board.cols // 2:
                break
            else:
                (ni, nj) = arr_to_pos(board, (i, j))
                moves.append(str_position(piece.position) + '-' + str_position((ni, nj)))
        else:
            break
    return moves


def process_captures(board: Board, piece: Piece) -> List[Piece]:
    """
    Find all pieces the moved piece can capture

    :param board: The board
    :param piece: The moved piece
    :return: The list of captured pieces
    """
    captures = []
    captures.extend(_process_captures(board, piece, 0, -1))  # left
    captures.extend(_process_captures(board, piece, 0, 1))  # right
    captures.extend(_process_captures(board, piece, -1, 0))  # up
    captures.extend(_process_captures(board, piece, 1, 0))  # down
    return captures


def _process_captures(board: Board, piece: Piece, inc_row: int, inc_col: int) -> List[Piece]:
    """
    Find all pieces the moved piece can capture along the selected axis

    :param board: The board
    :param piece: The moved piece
    :param inc_row: Trajectory: 1 for down, -1 for up, 0 for no change
    :param inc_col: Trajectory: 1 for left, -1 for right, 0 for no change
    :return: The list of captured pieces along the selected axis
    """
    captures = []
    i, j = pos_to_arr(board, piece.position)
    i += inc_row
    j += inc_col
    if not (out_of_board_arr(board, (i, j))):
        middle_piece = board.state[i, j]
        if middle_piece is not None:
            if (piece.type == DEFENDER and middle_piece.type == ATTACKER) or \
                    (piece.type == ATTACKER and middle_piece.type == DEFENDER):
                i += inc_row
                j += inc_col
                if not (out_of_board_arr(board, (i, j))):
                    outer_piece = board.state[i, j]
                    if outer_piece is not None and piece.type == outer_piece.type:
                        captures.append(middle_piece)

            elif piece.type == ATTACKER and middle_piece.type == KING:
                # case 1: king is on the throne, need 4 pieces
                # case 2: king is next to the throne, need 3 pieces
                if _check_king(board, middle_piece) == 4:
                    captures.append(middle_piece)
                # case 3: king is free roaming
                else:
                    x, y = pos_to_arr(board, middle_piece.position)
                    if not (x == board.rows // 2 and y == board.cols // 2):
                        i += inc_row
                        j += inc_col
                        if not (out_of_board_arr(board, (i, j))):
                            outer_piece = board.state[i, j]
                            if outer_piece is not None and piece.type == outer_piece.type:
                                captures.append(middle_piece)
    return captures


def _check_king(board: Board, king: Piece) -> int:
    """
    Check king's surrounding tiles for threats

    :param board: The board
    :param king: The king piece
    :return: The number of threatening tiles
    """
    threats = 0
    i, j = pos_to_arr(board, king.position)
    threats += __check_king(board, (i, j), 0, 1)
    threats += __check_king(board, (i, j), 0, -1)
    threats += __check_king(board, (i, j), 1, 0)  # down
    threats += __check_king(board, (i, j), -1, 0)  # up
    return threats


def __check_king(board: Board, king_arr: Tuple[int, int], row_inc: int, col_inc: int) -> int:
    """
    Check if king's neighbouring tile is threatening

    :param board: The board
    :param king_arr: The king position as array coordinates
    :param row_inc: Trajectory: 1 for down, -1 for up, 0 for no change
    :param col_inc: Trajectory: 1 for left, -1 for right, 0 for no change
    :return: 1 if the tile is threatening, 0 otherwise
    """
    i, j = king_arr
    i += row_inc
    j += col_inc
    if not out_of_board_arr(board, (i, j)):
        p = board.state[i, j]
        if p is not None:
            return 1 if p.type == ATTACKER else 0
        else:
            return 1 if i == board.rows // 2 and j == board.cols // 2 else 0
    else:
        return 0
