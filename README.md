# gym-tablut

The TablutEnv is an [OpenAI gym](https://gym.openai.com/) environment for reinforcement learning. In particular, it
implements the two-players, asymmetric, turn-based zero-sum board game of Tablut, a variant of the popular
game [Hnefatafl](https://en.wikipedia.org/wiki/Tafl_games).

## The Game
### The board
The board appears as follows:

![The board](gym_tablut/docs/board.png?raw=True)

With the following pieces already placed:
* the King: the middle piece in the middle, with the crown, sits on throne
* The Defenders: the white pieces surrounding the King in a cross formation
* The Attackers: the black pieces in a phalanx formation at each vertex of the cross

### Rules
The following rules are applied to the game:
- Each piece can move orthogonally as many tiles as desired, as long as it doesn't jump over any other piece.
- Only the king can land on and traverse the throne (central tile).
- A piece is captured if two enemy pieces land on its side. The king is armed and can partake in a capture.
- The king is captured by two enemy pieces on its side if it's not on or next to the throne, otherwise 4 pieces or 3 are
required, respectively.
- Threefold repetitions result in a loss

Note that the rules are slightly different from the Linneus' variant and the historical variant of Tablut.

### Goal of the game
The game is asymmetric in its goal:
- the Defender has to move its King so that it reaches any of the edges of the board
- the Attacker has to capture the fleeing king

The game also ends when no moves are available for the next player.

## The RL-side
### The actions
During the player's turn, the valid actions are generated and can be sampled in the environment's `action_space`; each action
corresponds to a move (`from_position-to_position`) that can be played.

Since the moves are generated deterministically from a given board configuration, they can be learned by an RL Agent.

### The rewards
This is a sparse reward environment, meaning most actions lead to a 0 reward. The following non-zero rewards are applied:

| Capture  | Reward for attacker | Reward for defender |
|:---------|:-------------------:|:-------------------:|
| Attacker | -1                  | +1                  |
| Defender | +2                  | -2                  |
| King     | +16                 | -16                 |

A draw results in 0 reward.

### The observations
After each move, the observation is the board state. This can be represented in two different ways:
1. A 2D matrix with the value of the piece on the tile (or 0 if there's no piece)
2. A 3D matrix with RGB values for each piece (see the [example below](README.md#Example run))

## Installation
You can install this environment by:
1. Downloading the repo: `git clone https://github.com/gallorob/gym-tablut.git`
2. Move in the repo's root folder: `cd gym-tablut`
3. Installing the requirements: `pip install -r requirements.txt`
4. Installing the environment: `pip install -e .`

## Example runs
The following are two episodes with a random agent, rendering with a pause of .05 seconds between each move.

### King escapes

![The match](gym_tablut/docs/ep_2.gif?raw=True)

And this are all the states that have been observed during the match:

![The states](gym_tablut/docs/ep_2.png?raw=True)

And this is the generated match result:
```
Match ended after 52 moves (ATK scored -14, DEF scored 14)
Reason: King has escaped
Last move: d6-a6
Remaining defenders: 7
Remaining attackers: 16
```

### King is captured

![The match](gym_tablut/docs/ep_4.gif?raw=True)

And this are all the states that have been observed during the match:

![The states](gym_tablut/docs/ep_4.png?raw=True)

And this is the generated match result:
```
Match ended after 57 moves (ATK scored 15, DEF scored -15)
Reason: King was captured
Last move: e9-e7
Remaining defenders: 8
Remaining attackers: 15
```

## Final notes
PRs are welcome and please quote this repo if you end up using it 😀