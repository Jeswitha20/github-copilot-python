import copy
from unittest.mock import patch

import pytest

import app


@pytest.fixture(autouse=True)
def reset_current_game():
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    yield
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as test_client:
        yield test_client


def test_index_renders_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'id="score-form"' in response.data
    assert b'id="leaderboard-body"' in response.data


def test_new_game_returns_puzzle_and_stores_solution(client):
    response = client.get('/new')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert app.CURRENT['puzzle'] == puzzle
    assert app.CURRENT['solution'] is not None


@pytest.mark.parametrize('difficulty, clues', [
    ('easy', 45),
    ('medium', 35),
    ('hard', 25),
])
def test_new_game_maps_difficulty_to_clue_count(client, difficulty, clues):
    puzzle = [[0 for _ in range(9)] for _ in range(9)]
    solution = [[1 for _ in range(9)] for _ in range(9)]

    with patch.object(app.sudoku_logic, 'generate_puzzle', return_value=(puzzle, solution)) as generate:
        response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    assert response.get_json() == {
        'puzzle': puzzle,
        'difficulty': difficulty,
        'clues': clues,
    }
    generate.assert_called_once_with(clues)


def test_new_game_defaults_to_medium(client):
    puzzle = [[0 for _ in range(9)] for _ in range(9)]
    solution = [[1 for _ in range(9)] for _ in range(9)]

    with patch.object(app.sudoku_logic, 'generate_puzzle', return_value=(puzzle, solution)) as generate:
        response = client.get('/new')

    assert response.status_code == 200
    assert response.get_json()['difficulty'] == 'medium'
    assert response.get_json()['clues'] == 35
    generate.assert_called_once_with(35)


def test_new_game_rejects_invalid_difficulty(client):
    with patch.object(app.sudoku_logic, 'generate_puzzle') as generate:
        response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid difficulty'}
    generate.assert_not_called()


def test_new_game_returns_error_when_generation_fails(client):
    with patch.object(
        app.sudoku_logic,
        'generate_puzzle',
        side_effect=ValueError('generation failed'),
    ):
        response = client.get('/new')

    assert response.status_code == 500
    assert response.get_json() == {'error': 'Unable to generate a puzzle'}


def test_difficulty_helper_returns_configured_clues():
    assert app.get_clues_for_difficulty('EASY') == 45
    assert app.get_clues_for_difficulty('medium') == 35
    assert app.get_clues_for_difficulty('hard') == 25


def test_difficulty_helper_rejects_invalid_values():
    with pytest.raises(ValueError, match='Invalid difficulty'):
        app.get_clues_for_difficulty('expert')

    with pytest.raises(ValueError, match='Invalid difficulty'):
        app.get_clues_for_difficulty(None)


def test_check_solution_requires_game_in_progress(client):
    response = client.post('/check', json={'board': []})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


@pytest.mark.parametrize('request_kwargs, expected_error', [
    ({}, 'Request body must be a JSON object'),
    ({'json': []}, 'Request body must be a JSON object'),
    ({'json': {}}, 'Missing board'),
    ({'json': {'board': [[0]]}}, 'board must be a 9x9 grid'),
    ({'json': {'board': [[0] * 9 for _ in range(8)]}}, 'board must be a 9x9 grid'),
])
def test_check_solution_validates_request_board(client, request_kwargs, expected_error):
    client.get('/new')

    response = client.post('/check', **request_kwargs)

    assert response.status_code == 400
    assert response.get_json() == {'error': expected_error}


def test_check_solution_rejects_invalid_cell_values(client):
    client.get('/new')
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 'invalid'

    response = client.post('/check', json={'board': board})

    assert response.status_code == 400
    assert response.get_json() == {
        'error': 'board cells must be integers from 0 to 9',
    }


def test_check_solution_returns_no_incorrect_cells_for_solution(client):
    client.get('/new')
    solution = copy.deepcopy(app.CURRENT['solution'])

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_solution_identifies_incorrect_cells(client):
    client.get('/new')
    solution = copy.deepcopy(app.CURRENT['solution'])
    solution[0][0] = solution[0][0] % 9 + 1

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert [0, 0] in response.get_json()['incorrect']
