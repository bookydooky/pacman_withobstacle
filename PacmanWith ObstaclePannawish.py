"""This game is similar to the Normal_pacman Pannawish.py however 
I add obstacles to the code so that the game can be a bit more challenging
(Players cannot move to cells containing obstacles).

Moreover, I modified the utility to comply with the obstacle added by
introducing an obstacle penalty, which increases as the player gets near the obstacles. 
This penalty reduces the utility if a player is near obstacles
, which encourage the players to avoid them. 
"""
#the code similar to NormalPacmanPannawish.py is explained in NormalPacmanPannawish.py
# the coments in this code are the things different in this code
import random
import copy

size = 8
coin_prob = 0.3 # prob of coin spawn
obstacle_prob = 0.08 # prob of obstacle spawn

coin = []
obstacles = []

player_positions = {"A": (0, 0), "B": (size - 1, size - 1)}
player_scores = {"A": 0, "B": 0}

board = [['-' for _ in range(size)] for _ in range(size)]

for i in range(size):
    for j in range(size):
        if random.random() < coin_prob:
            board[i][j] = 'o'
            coin.append((i, j))
        elif random.random() < obstacle_prob:
            board[i][j] = 'x'
            obstacles.append((i, j))

board[player_positions["A"][0]][player_positions["A"][1]] = "A"
board[player_positions["B"][0]][player_positions["B"][1]] = "B"

state = [board, player_positions, coin, player_scores, obstacles]
visited = [state]
player = "B"


def available_moves(state, current_player):
    current_pos = state[1][current_player]
    moves = ['up', 'down', 'left', 'right']
    if current_pos[0] == 0:
        moves.remove('up')
    if current_pos[0] == size - 1:
        moves.remove('down')
    if current_pos[1] == 0:
        moves.remove('left')
    if current_pos[1] == size - 1:
        moves.remove('right')
    return moves


def result(state, action, current_player):
    if current_player == "A":
        opponent = "B"
    else:
        opponent = "A"
    player_pos = state[1][current_player]
    opponent_pos = state[1][opponent]

    newboard = copy.deepcopy(state[0])
    newcoin = copy.deepcopy(state[2])
    newscore = {current_player: state[3][current_player], opponent: state[3][opponent]}

    if action == 'down':
        new_pos = (player_pos[0] + 1, player_pos[1])
    elif action == 'up':
        new_pos = (player_pos[0] - 1, player_pos[1])
    elif action == 'right':
        new_pos = (player_pos[0], player_pos[1] + 1)
    else:
        new_pos = (player_pos[0], player_pos[1] - 1)

    if new_pos == opponent_pos:
        return None
    elif new_pos in state[2]:
        newcoin.remove(new_pos)
        newscore[current_player] += 1

    if new_pos in state[4]:  # if new pos in obstacles return none so when the player check they will avoid moving in this direction
        return None

    newboard[new_pos[0]][new_pos[1]] = current_player
    newboard[player_pos[0]][player_pos[1]] = "-"

    new_player_position = {current_player: new_pos, opponent: opponent_pos}
    return [newboard, new_player_position, newcoin, newscore, state[4]]


def utility(state):
    player_score_A = state[3]["A"]
    player_score_B = state[3]["B"]
    
    player_A_pos = state[1]["A"]
    player_B_pos = state[1]["B"]
    
    total_distance_to_coins_A = sum(abs(player_A_pos[0] - coin[0]) + abs(player_A_pos[1] - coin[1]) for coin in state[2])
    total_distance_to_coins_B = sum(abs(player_B_pos[0] - coin[0]) + abs(player_B_pos[1] - coin[1]) for coin in state[2])
    
    # reduce the utility if there are obstacles near the player's position
    obstacle_penalty_A = sum(1 for obs in obstacles if abs(player_A_pos[0] - obs[0]) + abs(player_A_pos[1] - obs[1]) <= 1)
    obstacle_penalty_B = sum(1 for obs in obstacles if abs(player_B_pos[0] - obs[0]) + abs(player_B_pos[1] - obs[1]) <= 1)
    
    # Calculate utility for each player, considering score, distance from coins, and obstacle penalty
    player_A_utility = player_score_A + 2 / (1 + total_distance_to_coins_A) - 0.1*obstacle_penalty_A
    player_B_utility = player_score_B + 2 / (1 + total_distance_to_coins_B) - 0.1*obstacle_penalty_B
    # I multiply 0.1 to obstacle penaty to give more significant to the coin_distance to _player
    # As for the weight for each factor in the heuristic, I try modify it to get the best decision-making player
    return player_A_utility - player_B_utility



def terminal(state):
    if len(state[2]) == 0:
        return True
    return False


def maxValue(state, depth, alpha, beta, visited=[]):
    if terminal(state) or depth == 0:
        return utility(state)
    visited.append(state)
    v = float("-inf")
    for action in available_moves(state, "A"):
        r = result(state, action, "A")
        if r is None or r in visited:
            continue
        v = max(v, minValue(r, depth - 1, alpha, beta))
        if v >= beta:
            return v
        alpha = max(alpha, v)
    return v


def minValue(state, depth, alpha, beta, visited=[]):
    if terminal(state) or depth == 0:
        return utility(state)
    visited.append(state)
    v = float("inf")
    for action in available_moves(state, "B"):
        r = result(state, action, "B")
        if r is None or r in visited:
            continue
        v = min(v, maxValue(r, depth - 1, alpha, beta))
        if v <= alpha:
            return v
        beta = min(beta, v)
    return v


def minimax(state, player, depth, alpha, beta, visited):
    if terminal(state) or depth == 0:
        return None
    else:
        if player == "A":
            v = maxValue(state, depth, alpha, beta, visited)
            for action in available_moves(state, "A"):
                r = result(state, action, "A")
                if r is None or r in visited:
                    continue
                if minValue(r, depth - 1, alpha, beta) == v:
                    return action
        if player == "B":
            v = minValue(state, depth, alpha, beta, visited)
            for action in available_moves(state, "B"):
                r = result(state, action, "B")
                if r is None or r in visited:
                    continue
                if maxValue(r, depth - 1, alpha, beta) == v:
                    return action


def print_board(state):
    for x in range(size):
        for y in range(size):
            if (x, y) in state[1].values():
                if (x, y) == state[1]['A']:
                    print('A', end=' ')
                else:
                    print('B', end=' ')
            elif (x, y) in state[2]:
                print('o', end=' ')
            elif (x, y) in state[4]:  # Print obstacles
                print('x', end=' ')
            else:
                print('-', end=' ')
        print()
    print("Player positions:", state[1])
    print("Coin positions:", state[2])
    print("Score:", state[3])
    print("obstacles:",obstacles) # print list of obstacles position


print("Starting player:", player)
print_board(state)
print("---- Start ----")
print()

amountOfTurn = 0

while terminal(state) == False:
    if player == 'A':
        print("Turn A")
        action = minimax(state, 'A', 3, float("-inf"), float("inf"), visited)
        print("Action:", action)
        state = result(state, action, 'A')
        print_board(state)
        print()
        amountOfTurn += 1
        player = 'B'
    elif player == 'B':
        print("Turn B")
        action = minimax(state, 'B', 3, float("-inf"), float("inf"), visited)
        print("Action:", action)
        state = result(state, action, 'B')
        print_board(state)
        print()
        amountOfTurn += 1
        player = 'A'

print("---- End ----")
print("Amount of turns:", amountOfTurn)
print("Number of coins initially generated:", len(coin))
