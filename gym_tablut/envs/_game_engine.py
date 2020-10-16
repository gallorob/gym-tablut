from gym_tablut.envs._utils import *
from gym_tablut.envs.configs import *


class GameEngine:
    def __init__(self, variant: str):
        self.MAX_MOVES = 300
        self.known_variants = {
            'tablut': {
                'STARTING_PLAYER': ATK,
                'N_ROWS': 9,
                'N_COLS': 9,
                'MAX_REWARD': 100 + 16 + 16
            }
        }
        self.info = {}
        self.variant = variant
        assert variant in self.known_variants.keys(), f"[ERR GameEngine.__init__] Unknown variant {self.variant}"
        self.rules = self.known_variants.get(self.variant)
        self.STARTING_PLAYER = self.rules.get('STARTING_PLAYER')
        self.n_rows = self.rules.get('N_ROWS')
        self.n_cols = self.rules.get('N_COLS')
        self.vector_mask = vector_mask

    def fill_board(self, board: np.array):
        if self.variant == 'tablut':
            # add king
            board[4, 4] = KING
            # add defenders
            board[2, 4] = DEFENDER
            board[3, 4] = DEFENDER
            board[4, 2] = DEFENDER
            board[4, 3] = DEFENDER
            board[4, 5] = DEFENDER
            board[4, 6] = DEFENDER
            board[5, 4] = DEFENDER
            board[6, 4] = DEFENDER
            # add attackers
            board[0, 3] = ATTACKER
            board[0, 4] = ATTACKER
            board[0, 5] = ATTACKER
            board[1, 4] = ATTACKER
            board[3, 0] = ATTACKER
            board[3, 8] = ATTACKER
            board[4, 0] = ATTACKER
            board[4, 1] = ATTACKER
            board[4, 7] = ATTACKER
            board[4, 8] = ATTACKER
            board[5, 0] = ATTACKER
            board[5, 8] = ATTACKER
            board[7, 4] = ATTACKER
            board[8, 3] = ATTACKER
            board[8, 4] = ATTACKER
            board[8, 5] = ATTACKER

    def legal_moves(self, board: np.array, player: int):
        assert player in [ATK, DEF], f"[ERR: legal_moves] Unrecognized player type: {player}"
        moves = []
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                p = board[i, j]
                if p in [KING, ATTACKER, DEFENDER]:
                    if (p == ATTACKER and player == ATK) or \
                            (p != ATTACKER and player == DEF):
                        moves.extend(self._legal_moves(board, p, (i, j)))
        return moves

    @staticmethod
    def _legal_moves(board: np.array, piece: int, position: Tuple[int, int]) -> List[int]:
        """
        Compute the legal and valid moves for the selected piece in the given board

        :param board: The current board
        :param piece: The selected piece
        :param position: The selected piece position
        :return: A list of valid moves for the piece in the given board
        """
        moves = []
        for inc_i, inc_j in DIRECTIONS:
            i, j = position
            while True:
                i += inc_i
                j += inc_j
                if i < 0 or i > board.shape[0] - 1 or j < 0 or j > board.shape[1] - 1:
                    break
                t_tile = board[i, j]
                if t_tile == EMPTY:
                    moves.append(space_to_decimal(values=(position[0], position[1], i, j),
                                                  rows=board.shape[0],
                                                  cols=board.shape[1]))
                elif t_tile == THRONE:
                    if piece == KING:
                        moves.append(space_to_decimal(values=(position[0], position[1], i, j),
                                                      rows=board.shape[0],
                                                      cols=board.shape[1]))
                    else:
                        continue
                else:
                    break
        return moves

    @staticmethod
    def board_value(board: np.array) -> int:
        value = 0
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                p = board[i, j]
                if p == KING:
                    value += 16
                elif p == DEFENDER:
                    value += 2
                elif p == ATTACKER:
                    value -= 1
                else:
                    continue
        return value

    def alt_apply_move(self, board: np.ndarray, action: int) -> dict:
        move = decimal_to_space(action, board.shape[0], board.shape[1])
        return self.apply_move(board=board,
                               move=move)

    def apply_move(self, board: np.array, move: Tuple[int, int, int, int]) -> dict:
        fi, fj, ti, tj = move
        assert board[fi, fj] in [KING, ATTACKER, DEFENDER], \
            f"[ERR: apply_move] Selected invalid piece: {position_as_str(position=(fi, fj), rows=board.shape[0])}"
        assert board[ti, tj] not in [KING, ATTACKER, DEFENDER],\
            f"[ERR: apply_move] Invalid destination: {position_as_str(position=(ti, tj), rows=board.shape[0])}"
        info = {
            'game_over': False,
            'move': position_as_str((fi, fj), board.shape[0]).upper() + '-' + position_as_str((ti, tj),
                                                                                              board.shape[0]).upper(),
            'reward': 0
        }
        # update board and piece
        board[ti, tj] = board[fi, fj]
        board[fi, fj] = THRONE if on_throne_arr(board, (fi, fj)) else EMPTY
        # check if king has escaped
        if board[ti, tj] == KING and on_edge_arr(board, (ti, tj)):
            info['game_over'] = True
            info['reward'] += 100
        # process captures
        to_remove = self.process_captures(board, (ti, tj))
        for (i, j) in to_remove:
            if board[i, j] == KING:
                info['game_over'] = True
                info['reward'] += 100
            board[i, j] = THRONE if on_throne_arr(board, (i, j)) else EMPTY
            info['move'] += 'x' + position_as_str((i, j), board.shape[0]).upper()
        info['reward'] += self.board_value(board)
        # normalize rewards in [-1, 1]
        info['reward'] /= self.rules.get('MAX_REWARD')
        return info

    def process_captures(self, board: np.array, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        captures = []
        piece = board[position]
        for inc_i, inc_j in DIRECTIONS:
            i, j = position
            i += inc_i
            j += inc_j

            if not (out_of_board_arr(board, (i, j))):
                middle_piece = board[i, j]
                if middle_piece in [KING, ATTACKER, DEFENDER]:
                    if (piece == DEFENDER and middle_piece == ATTACKER) or \
                            (piece == KING and middle_piece == ATTACKER) or \
                            (piece == ATTACKER and middle_piece == DEFENDER):
                        i += inc_i
                        j += inc_j
                        if not (out_of_board_arr(board, (i, j))):
                            outer_piece = board[i, j]
                            # normal capture
                            if outer_piece in [KING, ATTACKER, DEFENDER] and \
                                    (piece == outer_piece or (piece == DEFENDER and outer_piece == KING)
                                     or (piece == KING and outer_piece == DEFENDER)):
                                captures.append((i - inc_i, j - inc_j))
                            # capture next to throne
                            elif outer_piece == THRONE and (
                                    (piece == ATTACKER and middle_piece == DEFENDER) or
                                    ((piece == DEFENDER or piece == KING) and piece == ATTACKER)):
                                captures.append((i - inc_i, j - inc_j))
                    # capture king
                    elif piece == ATTACKER and middle_piece == KING:
                        # case 1: king is on the throne, need 4 pieces
                        # case 2: king is next to the throne, need 3 pieces
                        if on_throne_arr(board, (i, j)) or next_to_throne_arr(board, (i, j)):
                            if self._check_king(board, (i, j)) == 4:
                                captures.append((i, j))
                        # case 3: king is free roaming
                        else:
                            i += inc_i
                            j += inc_j
                            if not (out_of_board_arr(board, (i, j))):
                                outer_piece = board[i, j]
                                if outer_piece == ATTACKER:
                                    captures.append((i - inc_i, j - inc_j))
        return captures

    @staticmethod
    def _check_king(board: np.array, position: Tuple[int, int]) -> int:
        threats = 0
        for inc_i, inc_j in DIRECTIONS:
            i, j = position
            i += inc_i
            j += inc_j
            if not out_of_board_arr(board, (i, j)):
                p = board[i, j]
                threats += 1 if p in [ATTACKER, THRONE] else 0
        return threats

    def check_endgame(self, last_moves: List[Tuple[int, int, int, int]], last_move: Tuple[int, int, int, int],
                      player: int, n_moves: int) -> dict:
        info = {
            'game_over': False,
            'reason': '',
            'reward': 0,
            'winner': DRAW
        }
        # check moves repetition
        if n_moves == self.MAX_MOVES:
            info['game_over'] = True
            info['reason'] = 'Moves limit reached'
            info['winner'] = ATK if player == DEF else DEF
        # check threefold repetition
        if check_threefold_repetition(last_moves=last_moves,
                                      last_move=last_move):
            info['game_over'] = True
            info['reason'] = 'Threefold repetition'
        return info
