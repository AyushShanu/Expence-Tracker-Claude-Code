# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py` or `flask run`
   - The app will be available at http://localhost:5001
3. Run tests: `pytest`
   - Note: Tests are not yet implemented; this project is a scaffold for student exercises
4. Linting: (Not configured yet - consider adding flake8 or pylint)
   - Example: `flake8 .` or `pylint app.py`

## Project Architecture

This is a Flask web application for expense tracking (Spendly) with the following structure:

- `app.py`: Main Flask application containing route definitions
- `templates/`: Jinja2 HTML templates for the frontend
  - `base.html`: Base template with common layout (navigation, footer)
  - Individual templates for each page (landing, login, register, terms, privacy)
- `static/`: Static assets (CSS, JavaScript)
  - `css/`: Stylesheets
  - `js/`: JavaScript files
- `database/`: Database layer (to be implemented by students)
  - `db.py`: Placeholder for database connection and initialization
- `requirements.txt`: Python dependencies (Flask, pytest, etc.)

### Key Components

1. **Application Factory Pattern**: The app is instantiated directly in app.py (simple approach for learning)
2. **Routing**: Routes are defined as Flask view functions in app.py
3. **Templates**: Jinja2 templating engine for HTML rendering
4. **Static Files**: Served from the `/static` endpoint
5. **Database**: Placeholder implementation in `database/db.py` (students implement `get_db()`, `init_db()`, `seed_db()`)

### Common Development Tasks

- **Running the application**: `python app.py` starts the development server on port 5001
- **Adding new routes**: Add functions in `app.py` with `@app.route` decorators
- **Creating templates**: Add HTML files in `templates/` folder, extending `base.html`
- **Adding static assets**: Place CSS in `static/css/`, JavaScript in `static/js/`
- **Database work**: Implement functions in `database/db.py` as indicated by the comments
- **Testing**: Write tests using pytest (test files should start with `test_`)
- **Running tests**: Execute `pytest` from the project root

### Code Conventions

- Follow PEP 8 for Python code style
- Templates use Jinja2 syntax with blocks for extending base layout
- Static files organized by type (css, js)
- Route functions should be concise and delegate business logic to service layers (when implemented)