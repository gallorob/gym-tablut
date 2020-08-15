from gym_tablut.envs._utils import *


class Tiles:
    def __init__(self):
        # tile values
        self.BACKGROUND = -1
        self.EMPTY = 0
        self.CORNER = 1
        self.THRONE = 2
        self.KING = 3
        self.DEFENDER = 4
        self.ATTACKER = 5


class Players:
    def __init__(self):
        # enum for current player
        self.DEF = 0
        self.ATK = 1
        self.DRAW = -1


class GameEngine:
    def __init__(self, variant: str):
        self.MAX_MOVES = 300
        self.tiles = Tiles()
        self.players = Players()
        self.known_variants = {
            'tablut': {
                'STARTING_PLAYER': self.players.ATK,
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

    def fill_board(self, board: np.array):
        if self.variant == 'tablut':
            # add king
            board[4, 4] = self.tiles.KING
            # add defenders
            board[2, 4] = self.tiles.DEFENDER
            board[3, 4] = self.tiles.DEFENDER
            board[4, 2] = self.tiles.DEFENDER
            board[4, 3] = self.tiles.DEFENDER
            board[4, 5] = self.tiles.DEFENDER
            board[4, 6] = self.tiles.DEFENDER
            board[5, 4] = self.tiles.DEFENDER
            board[6, 4] = self.tiles.DEFENDER
            # add attackers
            board[0, 3] = self.tiles.ATTACKER
            board[0, 4] = self.tiles.ATTACKER
            board[0, 5] = self.tiles.ATTACKER
            board[1, 4] = self.tiles.ATTACKER
            board[3, 0] = self.tiles.ATTACKER
            board[3, 8] = self.tiles.ATTACKER
            board[4, 0] = self.tiles.ATTACKER
            board[4, 1] = self.tiles.ATTACKER
            board[4, 7] = self.tiles.ATTACKER
            board[4, 8] = self.tiles.ATTACKER
            board[5, 0] = self.tiles.ATTACKER
            board[5, 8] = self.tiles.ATTACKER
            board[7, 4] = self.tiles.ATTACKER
            board[8, 3] = self.tiles.ATTACKER
            board[8, 4] = self.tiles.ATTACKER
            board[8, 5] = self.tiles.ATTACKER

    def legal_moves(self, board: np.array, player: int):
        assert player in [self.players.ATK, self.players.DEF], f"[ERR: legal_moves] Unrecognized player type: {player}"
        moves = []
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                p = board[i, j]
                if p in [self.tiles.KING, self.tiles.ATTACKER, self.tiles.DEFENDER]:
                    if (p == self.tiles.ATTACKER and player == self.players.ATK) or \
                            (p != self.tiles.ATTACKER and player == self.players.DEF):
                        moves.extend(self._legal_moves(board, p, (i, j)))
        return moves

    def _legal_moves(self, board: np.array, piece: int, position: Tuple[int, int]) -> List[int]:
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
                if t_tile == self.tiles.EMPTY:
                    moves.append(space_to_decimal(values=(position[0], position[1], i, j),
                                                  rows=board.shape[0],
                                                  cols=board.shape[1]))
                elif t_tile == self.tiles.THRONE:
                    if piece == self.tiles.KING:
                        moves.append(space_to_decimal(values=(position[0], position[1], i, j),
                                                      rows=board.shape[0],
                                                      cols=board.shape[1]))
                    else:
                        continue
                else:
                    break
        return moves

    def board_value(self, board: np.array) -> int:
        value = 0
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                p = board[i, j]
                if p == self.tiles.KING:
                    value += 16
                elif p == self.tiles.DEFENDER:
                    value += 2
                elif p == self.tiles.ATTACKER:
                    value -= 1
                else:
                    continue
        return value

    def apply_move(self, board: np.array, move: Tuple[int, int, int, int]) -> dict:
        fi, fj, ti, tj = move
        assert board[fi, fj] in [self.tiles.KING, self.tiles.ATTACKER, self.tiles.DEFENDER], \
            f"[ERR: apply_move] Selected invalid piece: {position_as_str(position=(fi, fj), rows=board.shape[0])}"
        assert board[ti, tj] not in [self.tiles.KING, self.tiles.ATTACKER, self.tiles.DEFENDER],\
            f"[ERR: apply_move] Invalid destination: {position_as_str(position=(ti, tj), rows=board.shape[0])}"
        info = {
            'game_over': False,
            'move': position_as_str((fi, fj), board.shape[0]).upper() + '-' + position_as_str((ti, tj),
                                                                                              board.shape[0]).upper(),
            'reward': 0
        }
        # update board and piece
        board[ti, tj] = board[fi, fj]
        board[fi, fj] = self.tiles.THRONE if on_throne_arr(board, (fi, fj)) else self.tiles.EMPTY
        # check if king has escaped
        if board[ti, tj] == self.tiles.KING and on_edge_arr(board, (ti, tj)):
            info['game_over'] = True
            info['reward'] += 100
        # process captures
        to_remove = self.process_captures(board, (ti, tj))
        for (i, j) in to_remove:
            if board[i, j] == self.tiles.KING:
                info['game_over'] = True
                info['reward'] += 100
            board[i, j] = self.tiles.THRONE if on_throne_arr(board, (i, j)) else self.tiles.EMPTY
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
                if middle_piece in [self.tiles.KING, self.tiles.ATTACKER, self.tiles.DEFENDER]:
                    if (piece == self.tiles.DEFENDER and middle_piece == self.tiles.ATTACKER) or \
                            (piece == self.tiles.KING and middle_piece == self.tiles.ATTACKER) or \
                            (piece == self.tiles.ATTACKER and middle_piece == self.tiles.DEFENDER):
                        i += inc_i
                        j += inc_j
                        if not (out_of_board_arr(board, (i, j))):
                            outer_piece = board[i, j]
                            # normal capture
                            if outer_piece in [self.tiles.KING, self.tiles.ATTACKER, self.tiles.DEFENDER] and \
                                    (piece == outer_piece or (piece == self.tiles.DEFENDER and outer_piece == self.tiles.KING)
                                     or (piece == self.tiles.KING and outer_piece == self.tiles.DEFENDER)):
                                captures.append((i - inc_i, j - inc_j))
                            # capture next to throne
                            elif outer_piece == self.tiles.THRONE and (
                                    (piece == self.tiles.ATTACKER and middle_piece == self.tiles.DEFENDER) or
                                    ((piece == self.tiles.DEFENDER or piece == self.tiles.KING) and piece == self.tiles.ATTACKER)):
                                captures.append((i - inc_i, j - inc_j))
                    # capture king
                    elif piece == self.tiles.ATTACKER and middle_piece == self.tiles.KING:
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
                                if outer_piece == self.tiles.ATTACKER:
                                    captures.append((i - inc_i, j - inc_j))
        return captures

    def _check_king(self, board: np.array, position: Tuple[int, int]) -> int:
        threats = 0
        for inc_i, inc_j in DIRECTIONS:
            i, j = position
            i += inc_i
            j += inc_j
            if not out_of_board_arr(board, (i, j)):
                p = board[i, j]
                threats += 1 if p in [self.tiles.ATTACKER, self.tiles.THRONE] else 0
        return threats

    def check_endgame(self, last_moves: List[Tuple[int, int, int, int]], last_move: Tuple[int, int, int, int],
                      player: int, n_moves: int) -> dict:
        info = {
            'game_over': False,
            'reason': '',
            'reward': 0,
            'winner': self.players.DRAW
        }
        # check moves repetition
        if n_moves == self.MAX_MOVES:
            info['game_over'] = True
            info['reason'] = 'Moves limit reached'
            info['winner'] = self.players.ATK if player == self.players.DEF else self.players.DEF
        # check threefold repetition
        if check_threefold_repetition(last_moves=last_moves,
                                      last_move=last_move):
            info['game_over'] = True
            info['reason'] = 'Threefold repetition'
        return info
