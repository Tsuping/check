import copy
import os
import time
import random
input = "input.txt"


def find_opponent(val):
    return 3 - val

def read_input(file):
    Board_size = 5
    info = []
    with open(file) as F:
        for lines in F.readlines():
            info.append(lines.strip())
    player = int(info[0])
    prev_board = []
    current_board = []
    for i in range(1, Board_size + 1):
        prev_board.append([int(value) for value in info[i]])
    for i in range(Board_size + 1, len(info)):
        current_board.append([int(value) for value in info[i]])
    return player, prev_board, current_board



def write_output(output_file, move):
    with open(output_file, 'w') as F:
        for item in move:
            F.write(item + " ")

def delete_tile(board, dead_piece_list):
    for piece in dead_piece_list:
        board[piece[0]][piece[1]] = 0
    return board


def ko_rule(current_board, prev_board):
    for i in range(5):
        for j in range(5):
            if current_board[i][j] != prev_board[i][j]:
                return False

    return True

def find_liberty(board, row, col):
    count = 0
    for point in find_ally_cluster(board, row, col):
        neighboring = find_neighbor(board, point[0], point[1])
        for check in neighboring:
            if board[check[0]][check[1]] == 0:
                count += 1
    return count

def find_dead_tile(board, player):
    dead_tile = list()
    for i in range(5):
        for j in range(5):
            if board[i][j] == player:
                if not find_liberty(board, i, j) and (i,j) not in dead_tile:
                    dead_tile.append((i,j))
    return dead_tile



def find_neighbor(board, i, j):
    neighbor = []
    board = delete_dead_tiles(board, (i, j))
    if i > 0:
        neighbor.append((i-1,j))
    if i < 4:
        neighbor.append((i+1,j))
    if j > 0:
        neighbor.append((i, j-1))
    if j < 4:
        neighbor.append((i, j+1))
    return neighbor


def find_neighbor_ally(board, i, j):
    allies = []
    for stones in find_neighbor(board, i, j):
        if board[i][j] == board[stones[0]][stones[1]]:
            allies.append(stones)
    return allies


def find_ally_cluster(board, i, j):
    ally_cluster = list()
    queue = []
    queue.append((i, j))
    while queue:
        node = queue.pop()
        ally_cluster.append((node[0], node[1]))
        for neighbor in find_neighbor_ally(board, node[0], node[1]):
            if neighbor not in queue and neighbor not in ally_cluster:
                queue.append(neighbor)
    return ally_cluster

def delete_dead_tiles(board, player):
    check = find_dead_tile(board, player)
    if len(check) == 0:
        return board
    new_board = delete_tile(board, check)
    return new_board

def good_move(curr_board, prev_board, player, i, j):
    if curr_board[i][j] != 0:
        return False
    copy_board = copy.deepcopy(curr_board)
    copy_board[i][j] = player
    dead_anemy_tile = find_dead_tile(copy_board, find_opponent(player))
    copy_board = delete_dead_tiles(copy_board, find_opponent)
    if find_liberty(copy_board, i, j) >= 1 and not (dead_anemy_tile and ko_rule(copy_board, prev_board)):
        return True


def find_valid_move(curr_board, prev_board, player):
    moves = []
    for i in range(5):
        for j in range(5):
            if good_move(curr_board, prev_board, player, i, j):
                moves.append((i, j))
    return moves

def next_state_movement(board, position, player):
    new_board = copy.deepcopy(board)
    new_board[position[0]][position[1]] = player
    new_board = delete_dead_tiles(new_board, find_opponent(player))
    return new_board

def find_rewards(board, va):
    our_agent = 0
    opponent_agent = 0
    our_agent_potential_reward = 0
    opponent_agent_potnetial_reward = 0
    for i in range(5):
        for j in range(5):
            if board[i][j] == player:
                our_agent += 1
                liberty_count = find_liberty(board, i, j)
                our_agent_potential_reward = our_agent_potential_reward + our_agent + liberty_count
            elif board[i][j] == find_opponent(player):
                opponent_agent += 1
                liberty_count = find_liberty(board, i, j)
                opponent_agent_potnetial_reward = opponent_agent_potnetial_reward + opponent_agent + liberty_count
    value = our_agent_potential_reward - opponent_agent_potnetial_reward
    if va == player:
        return value
    else:
        return -1 * value

def Minmax(curr_board, prev_board, depth, alpha, beta, next_player):
    if depth == 0:
        return 
    suggest_moves = []
    highest_score = 0
    current_board_copy = copy.deepcopy(curr_board)
    for moves in find_valid_move(curr_board, prev_board, next_player):
        next_state_board = next_state_movement(curr_board, moves, next_player)
        dfs_search_min = min_part(next_state_board, current_board_copy, depth-1, alpha, beta, find_opponent(next_player))
        if dfs_search_min > highest_score or not suggest_moves:
            highest_score = dfs_search_min
            alpha = highest_score
            suggest_moves = [moves]
        elif dfs_search_min == highest_score:
            suggest_moves.append(moves)

    return suggest_moves
    


def min_part(curr_board, prev_board, depth, alpha, beta, next_player):
    heuristic_value = find_rewards(curr_board, next_player)
    if depth == 0:
        return heuristic_value
    curr_board_copy = copy.deepcopy(curr_board)
    for moves in find_valid_move(curr_board, prev_board, next_player):
        next_state_board = next_state_movement(curr_board, moves, next_player)
        current_value = max_part(next_state_board, curr_board_copy, depth - 1, alpha, beta, next_player)
        if current_value < heuristic_value:
            heuristic_value = current_value
        

    return heuristic_value

def max_part(curr_board, prev_board, depth, alpha, beta, next_player):
    v = -1000
    heuristic_value = find_rewards(curr_board, next_player)
    if depth == 0:
        return heuristic_value
    curr_board_copy = copy.deepcopy(curr_board)
    for moves in find_valid_move(curr_board, prev_board, next_player):
        next_state_board = next_state_movement(curr_board, moves, next_player)
        current_value = min_part(next_state_board, curr_board_copy, depth - 1, alpha, beta, next_player)
        if current_value > heuristic_value:
            heuristic_value = current_value

    return heuristic_value


        
        
    
def minimax(curr_board, prev_board, depth, next_player, alpha, beta, isMax):
    curr_ans = []
    heur = find_rewards(curr_board, next_player)
    if depth == 0:
        return heur, None

    if isMax:
        maxval = float("-inf")
        current_board_copy = copy.deepcopy(curr_board)
        all_moves = find_valid_move(curr_board, prev_board, next_player)
        for moves in all_moves:
            next_state = next_state_movement(curr_board, moves, next_player)
            value = minimax(next_state, current_board_copy, depth - 1, find_opponent(next_player), alpha, beta, False)
            if maxval < value[0] or not curr_ans:
                maxval = value[0]
                alpha = max(alpha, maxval)
                if alpha > beta:
                    
                    break
                curr_ans = [moves]
            elif maxval == value[0]:
                curr_ans.append(moves)
        if curr_ans == None:
            return maxval, None
        return maxval, curr_ans
    else:
        minval = float('inf')
        current_board_copy = copy.deepcopy(curr_board)
        all_moves = find_valid_move(curr_board, prev_board, next_player)
        for moves in all_moves:
            next_state = next_state_movement(curr_board, moves, next_player)
            value = minimax(next_state, current_board_copy, depth - 1, find_opponent(next_player), alpha, beta, True)
            if minval > value[0] or not curr_ans:
                minval = value[0]
                beta = min(beta, minval)
                if alpha > beta:
                    break
                curr_ans = [moves]
            elif minval == value[0]:
                curr_ans.append(moves)
        if curr_ans == None:
            return minval, None
        return minval, curr_ans


player, prev_board, current_board = read_input(input)

# start_time = time.time()
# print(minimax(current_board, prev_board, 4, player, -1000, 1000, True))
# print("--- %s seconds ---" % (time.time() - start_time))

# print("\n")
# start_time = time.time()
# print(Minmax(current_board, prev_board, 2, -1000, 1000, player))
# print("--- %s seconds ---" % (time.time() - start_time))
f2 = open("output.txt", "w+")
count = 0
for i in range(5):
    for j in range(5):
        if current_board[i][j] != 0:
            count += 1
if count == 0 and player == 1:
    moves = [(2,2)]
else:
    move = minimax(current_board, prev_board, 4, player, -1000, 1000, True)
    moves = move[1]

if moves == []:

    f2.write("PASS")
else:
    rand_best = random.choice(moves)
    f2.write("%d%s%d" % (rand_best[0], ",", rand_best[1]))