import pytest
import tempfile
import os
from app import app as flask_app
from database.db import init_db, get_db
from database.queries import get_user_by_id
import sqlite3

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Use an in-memory database for testing
    # We need to override the get_db function to use our test database
    # We'll create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Override the database configuration
    original_config = flask_app.config.copy()
    flask_app.config['DATABASE'] = db_path
    flask_app.config['TESTING'] = True

    # Override the get_db function in database/db.py to use our test database
    import database.db as db_module
    original_get_db = db_module.get_db

    def get_test_db():
        # If we don't have a connection, create one
        if not hasattr(g, 'sqlite_db'):
            g.sqlite_db = sqlite3.connect(
                flask_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.sqlite_db.row_factory = sqlite3.Row
        return g.sqlite_db

    # We need to use Flask's g object, so we need to import g
    from flask import g

    # Replace the get_db function
    db_module.get_db = get_test_db

    # Initialize the database
    with flask_app.app_context():
        init_db()
        seed_db()

    yield flask_app

    # Restore the original get_db function
    db_module.get_db = original_get_db

    # Restore the original config
    flask_app.config.clear()
    flask_app.config.update(original_config)

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()