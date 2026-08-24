import copy
import random

SIZE = 9
EMPTY = 0
MAX_REMOVAL_ATTEMPTS = 10

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def _is_complete_valid(board):
    expected = set(range(1, SIZE + 1))
    for row in range(SIZE):
        if set(board[row]) != expected:
            return False
    for col in range(SIZE):
        if {board[row][col] for row in range(SIZE)} != expected:
            return False
    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            values = {
                board[row][col]
                for row in range(start_row, start_row + 3)
                for col in range(start_col, start_col + 3)
            }
            if values != expected:
                return False
    return True

def _count_solutions(board, limit):
    best_cell = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                candidates = [
                    candidate
                    for candidate in range(1, SIZE + 1)
                    if is_safe(board, row, col, candidate)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates

    if best_cell is None:
        return 1 if _is_complete_valid(board) else 0

    row, col = best_cell
    solution_count = 0
    for candidate in best_candidates:
        board[row][col] = candidate
        solution_count += _count_solutions(board, limit - solution_count)
        board[row][col] = EMPTY
        if solution_count >= limit:
            return solution_count
    return solution_count

def count_solutions(board, limit=2):
    if limit < 1:
        raise ValueError('limit must be at least 1')
    return _count_solutions(deep_copy(board), limit)

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    removals_needed = SIZE * SIZE - clues

    for _ in range(MAX_REMOVAL_ATTEMPTS):
        candidate = deep_copy(board)
        cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
        random.shuffle(cells)
        removals = 0

        for row, col in cells:
            if removals == removals_needed:
                board[:] = candidate
                return

            original = candidate[row][col]
            if original == EMPTY:
                continue
            candidate[row][col] = EMPTY
            if count_solutions(candidate) == 1:
                removals += 1
            else:
                candidate[row][col] = original

    raise ValueError('Unable to generate a uniquely solvable puzzle with the requested clues')

def generate_puzzle(clues=35):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
