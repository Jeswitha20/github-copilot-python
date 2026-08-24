// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuLeaderboard';
const THEME_KEY = 'sudokuTheme';
const VALID_DIFFICULTIES = new Set(['easy', 'medium', 'hard']);
let puzzle = [];
let currentDifficulty = 'medium';
let gameStartedAt = null;
let gameCompleted = false;
let moveValidationRequest = 0;

function setDarkMode(enabled) {
  document.body.classList.toggle('dark-theme', enabled);
  const toggle = document.getElementById('dark-mode-toggle');
  toggle.setAttribute('aria-pressed', String(enabled));
  toggle.textContent = enabled ? 'Light mode' : 'Dark mode';
  try {
    localStorage.setItem(THEME_KEY, enabled ? 'dark' : 'light');
  } catch (error) {
    return;
  }
}

function initializeTheme() {
  let enabled = false;
  try {
    enabled = localStorage.getItem(THEME_KEY) === 'dark';
  } catch (error) {
    enabled = false;
  }
  setDarkMode(enabled);
}

function readLeaderboard() {
  try {
    const stored = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');
    if (!Array.isArray(stored)) return [];
    return stored
      .filter((score) => score && typeof score.name === 'string'
        && score.name.trim() && Number.isFinite(score.time)
        && score.time >= 0 && VALID_DIFFICULTIES.has(score.difficulty))
      .map((score) => ({
        name: score.name.trim().slice(0, 40),
        time: score.time,
        difficulty: score.difficulty,
      }))
      .sort((first, second) => first.time - second.time)
      .slice(0, 10);
  } catch (error) {
    return [];
  }
}

function writeLeaderboard(scores) {
  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores));
  } catch (error) {
    return false;
  }
  return true;
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function renderLeaderboard() {
  const leaderboardBody = document.getElementById('leaderboard-body');
  leaderboardBody.innerHTML = '';
  readLeaderboard().forEach((score, index) => {
    const row = document.createElement('tr');
    [index + 1, score.name, formatTime(score.time), score.difficulty].forEach((value) => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.appendChild(cell);
    });
    leaderboardBody.appendChild(row);
  });
}

function readBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const value = inputs[i * SIZE + j].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

async function validateMove(input) {
  const value = input.value;
  input.classList.remove('incorrect', 'correct-entry');
  if (!value || input.disabled) return;

  const requestId = ++moveValidationRequest;
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  try {
    const res = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: readBoard()}),
    });
    const data = await res.json();
    if (requestId !== moveValidationRequest || input.value !== value) return;
    const isIncorrect = data.incorrect && data.incorrect.some(
      (position) => position[0] === row && position[1] === col
    );
    const message = document.getElementById('message');
    if (isIncorrect) {
      input.classList.add('incorrect');
      message.className = 'immediate-error';
      message.innerText = 'That move is incorrect.';
    } else if (data.incorrect) {
      input.classList.add('correct-entry');
      message.className = 'immediate-success';
      message.innerText = 'Move looks good.';
    }
  } catch (error) {
    // The Check button remains available if immediate validation is unavailable.
  }
}

function saveScore(name, time, difficulty) {
  const scores = readLeaderboard();
  scores.push({name: name.trim().slice(0, 40), time, difficulty});
  scores.sort((first, second) => first.time - second.time);
  writeLeaderboard(scores.slice(0, 10));
  renderLeaderboard();
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        validateMove(e.target);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }
  currentDifficulty = data.difficulty || difficulty;
  renderPuzzle(data.puzzle);
  gameStartedAt = performance.now();
  gameCompleted = false;
  moveValidationRequest++;
  document.getElementById('score-form').hidden = true;
  document.getElementById('player-name').value = '';
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = readBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.className = 'error-message';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    msg.className = 'success-message';
    if (!gameCompleted) {
      gameCompleted = true;
      const completionTime = Math.max(0, Math.round((performance.now() - gameStartedAt) / 1000));
      msg.innerText = `Congratulations! You solved it in ${formatTime(completionTime)}.`;
      document.getElementById('score-form').hidden = false;
      document.getElementById('score-form').dataset.time = completionTime;
    }
  } else {
    msg.className = 'error-message';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  initializeTheme();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('dark-mode-toggle').addEventListener('click', () => {
    setDarkMode(!document.body.classList.contains('dark-theme'));
  });
  document.getElementById('score-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const name = document.getElementById('player-name').value.trim();
    if (!name) return;
    saveScore(name, Number(form.dataset.time), currentDifficulty);
    form.hidden = true;
    document.getElementById('message').innerText = 'Score saved!';
  });
  renderLeaderboard();
  // initialize
  newGame();
});