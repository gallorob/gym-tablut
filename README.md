# gym-tablut

The TablutEnv is an [OpenAI gym](https://gym.openai.com/) environment for reinforcement learning. In particular, it
implements the two-players, asymmetric, turn-based board game of Tablut, a variant of the popular
game [Hnefatafl](https://en.wikipedia.org/wiki/Tafl_games).

## The board
The board appears as follows:

![The board](gym_tablut/docs/board.png?raw=True)

With the following pieces already placed:
* the King: the middle piece in the middle, with the crown, sits on throne
* The defenders: the white pieces surrounding the King in a cross formation
* The attackers: the black pieces in a phalanx formation at each vertex of the cross

### Rules
The following rules are applied to the game:
- Each piece can move orthogonally as many tiles as desired, as long as it doesn't jump over any other piece.
- Only the king can land on and traverse the throne (central tile).
- A piece is captured if two enemy pieces land on its side. The king is unarmed and can't partake in a capture.
- The king is captured by two enemy pieces on its side if it's not on or next to the throne, otherwise 4 pieces or 3 are
required, respectively.
- Threefold repetitions result in a loss (TODO)

Note that the rules are slightly different from the Linneus' variant and the historical variant of Tablut.

### Goal of the game
The game is asymmetric in its goal:
- the defender has to move it king so that it reaches any of the edge of the board
- the attacker has to capture the fleeing king

The game also ends when no moves are available for the next player.

Draws are not allowed.

## The actions
During the player's turn, the valid actions are generated and can be sampled in the environment's `action_space`; each action
corresponds to a move (`from_position-to_position`) that can be played.

## The rewards
This is a sparse reward environment, meaning most actions lead to a 0 reward. The following non-zero rewards are applied:

| Capture  | Reward for attacker | Reward for defender |
|:---------|:-------------------:|:-------------------:|
| Attacker | -1                  | +1                  |
| Defender | +2                  | -2                  |
| King     | +16                 | -16                 |
