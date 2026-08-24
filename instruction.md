# GitHub Copilot Instructions

## Project Overview

This project is a Flask-based Sudoku game developed as part of the "Refactoring Legacy Code with Copilot" project.

The application consists of:

* Python Flask backend
* Sudoku generation and validation logic
* HTML templates
* JavaScript for interactive game functionality
* CSS for responsive and accessible styling
* Pytest tests for backend and Sudoku logic

## Coding Standards

* Use clear, descriptive names for variables, functions, and classes.
* Follow PEP 8 conventions for Python code.
* Use 4 spaces for Python indentation.
* Keep functions focused on a single responsibility.
* Prefer small, reusable functions over large functions.
* Add comments only when they clarify non-obvious logic.
* Avoid unnecessary duplication.
* Preserve existing functionality when refactoring legacy code.
* Do not introduce unnecessary dependencies.

## Python and Flask Guidelines

* Use Flask for HTTP routing and server-side application logic.
* Keep Sudoku algorithms in `sudoku_logic.py` rather than placing them directly in Flask routes.
* Keep Flask route handlers focused on request handling and responses.
* Validate user-provided request parameters.
* Return appropriate HTTP status codes for invalid requests.
* Do not expose internal implementation details or the Sudoku solution unnecessarily.

## Sudoku Logic Guidelines

* The Sudoku board is a 9x9 grid.
* `0` represents an empty cell.
* A valid Sudoku move must satisfy row, column, and 3x3 box constraints.
* Every generated puzzle must have exactly one valid solution.
* Solution-counting should stop after detecting two solutions because only uniqueness is required.
* Do not modify the original board unexpectedly when performing solution-counting or validation.
* Difficulty should control the number of prefilled cells:

  * Easy: 45 clues
  * Medium: 35 clues
  * Hard: 25 clues

## Frontend Guidelines

* Keep HTML structure semantic and readable.
* Use JavaScript for client-side interaction and UI updates.
* Keep CSS organized and responsive.
* The Sudoku board must remain usable on desktop and mobile devices.
* Maintain readable contrast in both light and dark modes.
* Keep the 3x3 Sudoku blocks visually distinguishable.
* Do not reveal the correct solution when displaying invalid-move feedback.
* Preserve locked prefilled Sudoku cells.

## Testing Guidelines

* Use `pytest` for Python tests.
* Run the complete test suite after significant code changes.
* Do not remove or weaken existing tests simply to make them pass.
* Add tests when introducing important new functionality.
* Test both normal behavior and relevant edge cases.
* Keep tests independent and avoid unnecessary reliance on randomness.
* Use mocks when testing Flask routes where real Sudoku generation is unnecessary.

Run the tests from the `starter` directory with:

```bash
python -m pytest
```

## GitHub Copilot Usage Guidelines

When using GitHub Copilot:

1. Inspect the existing code before making changes.
2. Prefer small, focused changes instead of rewriting the entire application.
3. Ask Copilot to explain unfamiliar code or suggestions before accepting them.
4. Review generated code for correctness, security, maintainability, and compatibility with the existing project.
5. Do not blindly accept generated code.
6. Preserve existing working functionality during refactoring.
7. Run the test suite after every significant change.
8. Add or update tests when introducing important functionality.
9. Use Copilot to investigate errors rather than hiding or bypassing them.
10. Document significant Copilot interactions with screenshots when required by the project.

## Project Architecture

Use the following separation of responsibilities:

* `app.py` — Flask application, routes, request handling, and application state.
* `sudoku_logic.py` — Sudoku generation, validation, solving, and uniqueness logic.
* `templates/` — HTML templates.
* `static/main.js` — browser-side game interaction and UI behavior.
* `static/styles.css` — application styling and responsive layout.
* `tests/` — automated Python tests.
* `Screenshots/` — screenshots documenting Copilot usage and testing.

Avoid moving Sudoku algorithm logic into frontend JavaScript or Flask route handlers unless there is a clear reason.

## Refactoring Principles

When modernizing legacy code:

* First understand the existing behavior.
* Preserve working behavior unless a requirement explicitly requires changing it.
* Prefer clear and maintainable code over unnecessarily complex abstractions.
* Avoid changing multiple unrelated components in a single refactoring step.
* Run tests before and after significant refactoring.
* Keep the application architecture understandable for future developers.

## Refactoring and Modernization Guidelines

When refactoring legacy code, follow these practices:

### Modular and Reusable Components

- Break large or multi-purpose functions into smaller functions with a single responsibility.
- Keep Flask route handlers focused on HTTP request handling and response generation.
- Keep Sudoku algorithms and validation logic in `sudoku_logic.py`.
- Extract repeated logic into reusable helper functions instead of duplicating code.
- Prefer clear function interfaces and avoid unnecessary global state.
- Use descriptive function and variable names.
- Avoid creating large monolithic functions.

### Error Handling

- Validate external and user-provided input before processing it.
- Use Python `try`/`except` blocks where operations can reasonably raise exceptions.
- Do not use broad `except Exception` blocks unless there is a specific reason and the error is handled appropriately.
- Return clear and consistent error responses from Flask routes.
- Handle malformed JSON, invalid parameters, and unexpected application states gracefully.
- Do not expose sensitive implementation details in error messages.
- Provide useful fallback behavior where appropriate.

### Comments and Documentation

- Add comments when they explain non-obvious algorithms or design decisions.
- Avoid comments that simply restate what the code already says.
- Document important public functions using clear docstrings where appropriate.
- Explain complex Sudoku algorithms, particularly recursive solution counting and uniqueness validation.
- Keep comments and documentation consistent with the current implementation.

### Testing and Validation

- Run the existing test suite before and after significant refactoring.
- Do not modify application behavior solely to make a test pass.
- Add tests for important new functionality and edge cases.
- Verify that the Flask application starts successfully after refactoring.
- Perform manual testing of important user-facing features.
- Use `python -m pytest` from the `starter` directory to run the automated tests.

### Refactoring Workflow

1. Understand the existing legacy implementation.
2. Establish baseline tests.
3. Identify responsibilities that can be separated.
4. Make small, focused refactoring changes.
5. Preserve existing behavior unless a requirement requires a change.
6. Run tests after each significant change.
7. Review generated Copilot code before accepting it.
8. Document important Copilot-assisted decisions.
9. Verify the application manually after refactoring.
