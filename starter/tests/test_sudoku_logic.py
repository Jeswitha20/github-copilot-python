import pytest

import sudoku_logic


def is_valid_solution(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))
    rows = [set(row) for row in board]
    columns = [
        {board[row][column] for row in range(sudoku_logic.SIZE)}
        for column in range(sudoku_logic.SIZE)
    ]
    boxes = [
        {
            board[row][column]
            for row in range(box_row, box_row + 3)
            for column in range(box_column, box_column + 3)
        }
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_column in range(0, sudoku_logic.SIZE, 3)
    ]
    return all(values == expected for values in rows + columns + boxes)


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_is_independent_of_original():
    board = sudoku_logic.create_empty_board()
    copied_board = sudoku_logic.deep_copy(board)

    copied_board[0][0] = 7

    assert board[0][0] == sudoku_logic.EMPTY
    assert copied_board[0][0] == 7


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    assert not sudoku_logic.is_safe(board, 1, 0, 5)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)
    assert sudoku_logic.is_safe(board, 1, 1, 6)


def test_find_incorrect_cells_returns_changed_coordinates():
    solution = [list(range(1, sudoku_logic.SIZE + 1)) for _ in range(sudoku_logic.SIZE)]
    board = sudoku_logic.deep_copy(solution)
    board[0][0] = sudoku_logic.EMPTY
    board[4][7] = sudoku_logic.EMPTY

    assert sudoku_logic.find_incorrect_cells(board, solution) == [[0, 0], [4, 7]]


def test_fill_board_creates_a_complete_valid_solution():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert is_valid_solution(board)


def test_count_solutions_returns_one_for_completed_valid_board():
    board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    assert sudoku_logic.count_solutions(board) == 1


def test_count_solutions_rejects_completed_invalid_board():
    board = [[1 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]

    assert sudoku_logic.count_solutions(board) == 0


def test_count_solutions_detects_multiple_solutions():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(board) == 2


def test_count_solutions_does_not_modify_input():
    board = sudoku_logic.create_empty_board()
    original = sudoku_logic.deep_copy(board)

    sudoku_logic.count_solutions(board)

    assert board == original


def test_count_solutions_returns_one_for_known_unique_puzzle():
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    assert sudoku_logic.count_solutions(board) == 1


def test_generate_puzzle_returns_solution_and_requested_number_of_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert is_valid_solution(solution)
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert all(
        puzzle[row][column] in (sudoku_logic.EMPTY, solution[row][column])
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )
    assert sudoku_logic.count_solutions(puzzle) == 1


def test_generate_puzzle_rejects_clues_outside_board_size():
    with pytest.raises(ValueError, match='between 0 and 81'):
        sudoku_logic.generate_puzzle(-1)

    with pytest.raises(ValueError, match='between 0 and 81'):
        sudoku_logic.generate_puzzle(82)
