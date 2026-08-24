from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

DIFFICULTIES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}


def get_clues_for_difficulty(difficulty):
    """Return the configured clue count for a supported difficulty."""
    if not isinstance(difficulty, str):
        raise ValueError('Invalid difficulty')
    try:
        return DIFFICULTIES[difficulty.lower()]
    except KeyError:
        raise ValueError('Invalid difficulty') from None


def error_response(message, status_code):
    """Build the consistent JSON error response used by the API routes."""
    return jsonify({'error': message}), status_code


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium')
    try:
        clues = get_clues_for_difficulty(difficulty)
    except ValueError as error:
        return error_response(str(error), 400)

    try:
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
    except ValueError:
        return error_response('Unable to generate a puzzle', 500)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({
        'puzzle': puzzle,
        'difficulty': difficulty,
        'clues': clues,
    })


@app.route('/check', methods=['POST'])
def check_solution():
    solution = CURRENT.get('solution')
    if solution is None:
        return error_response('No game in progress', 400)

    if not request.is_json:
        return error_response('Request body must be a JSON object', 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response('Request body must be a JSON object', 400)
    if 'board' not in data:
        return error_response('Missing board', 400)

    try:
        incorrect = sudoku_logic.find_incorrect_cells(data['board'], solution)
    except ValueError as error:
        return error_response(str(error), 400)
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)