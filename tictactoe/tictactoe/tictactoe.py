"""
Tic Tac Toe Player
"""

from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    not_empty = [1 for row in board for elem in row if elem != EMPTY]
    if sum(not_empty) % 2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possibilities = set()
    for (i,row) in enumerate(board):
        for (j,elem) in enumerate(row):
            if elem == EMPTY:
                possibilities.add((i,j))
    return possibilities

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    solution = deepcopy(board)
    for (i, row) in enumerate(solution):
        for (j, elem) in enumerate(row):
            if (i,j) == action and board[i][j] == EMPTY:
                solution[i][j] = player(board)
            elif (i,j) == action and board[i][j] != EMPTY:
                raise Exception("Not empty cell, move forbidden")
    return solution


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if board[0][0] == board[1][0] == board[2][0]:
        return board[0][0]
    elif board[0][0] == board[0][1] == board[0][2]:
        return board[0][0]
    elif board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    elif board[1][0] == board[1][1] == board[1][2]:
        return board[1][0]
    elif board[2][0] == board[2][1] == board[2][2]:
        return board[2][0]
    elif board[0][1] == board[1][1] == board[2][1]:
        return board[0][1]
    elif board[0][2] == board[1][2] == board[2][2]:
        return board[0][2]
    elif board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if board[0][0] == board[1][0] == board[2][0] != EMPTY:
        return True
    elif board[0][0] == board[0][1] == board[0][2] != EMPTY:
        return True
    elif board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return True
    elif board[1][0] == board[1][1] == board[1][2] != EMPTY:
        return True
    elif board[2][0] == board[2][1] == board[2][2] != EMPTY:
        return True
    elif board[0][1] == board[1][1] == board[2][1] != EMPTY:
        return True
    elif board[0][2] == board[1][2] == board[2][2] != EMPTY:
        return True
    elif board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return True
    elif all([x == O or x == X for row in board for x in row]):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def last_results_f(board):
    """
    Return a list of possible last results with the given board
    """
    if terminal(board):
        return [utility(board)]
    last_results = []
    next_actions = actions(board)
    for action in next_actions:
        new_board = result(board, action)
        if terminal(new_board):
            last_results.append(utility(new_board))
            continue
        next_l = last_results_f(new_board)
        last_results.extend(next_l)
    return last_results


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    next_actions = actions(board)
    results = []
    for action in next_actions:
        new_board = result(board, action)
        last_result = last_results_f(new_board)
        results.append(last_result)
    sum_utilities = []
    for elem in results:
        sum_utilities.append(sum(elem))
    if player(board) == O:
        tgt = min(range(len(sum_utilities)), key=sum_utilities.__getitem__)
    else:
        tgt = max(range(len(sum_utilities)), key=sum_utilities.__getitem__)
    for ind, act in enumerate(next_actions):
        if ind == tgt:
            return act