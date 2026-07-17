import sqlite3
import os
from flask import g
from werkzeug.security import generate_password_hash

def get_db():
    """Return a SQLite database connection with row factory and foreign keys enabled."""
    if 'db' not in g:
        # Determine the database file path
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'expense_tracker.db'
        )
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # Enable foreign key constraints
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def init_db():
    """Create database tables if they don't exist."""
    db = get_db()
    cursor = db.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date DATE NOT NULL,
            category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
        )
    ''')

    db.commit()

def seed_db():
    """Insert sample data for development."""
    db = get_db()
    cursor = db.cursor()

    # Check if we already have a user to avoid duplicates
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        return  # Database already seeded

    # Hash the password for the demo user
    password_hash = generate_password_hash('demo123')

    # Insert demo user
    cursor.execute('''
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    ''', ('Demo User', 'demo@example.com', password_hash))

    user_id = cursor.lastrowid

    # Insert default categories for the demo user
    categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Education', 'Other']
    category_ids = {}
    for category in categories:
        cursor.execute('''
            INSERT INTO categories (name, user_id)
            VALUES (?, ?)
        ''', (category, user_id))
        category_ids[category] = cursor.lastrowid

    # Insert sample expenses
    from datetime import date, timedelta
    today = date.today()

    expenses_data = [
        # Food expenses
        (user_id, 12.50, 'Lunch at cafe', today, category_ids['Food']),
        (user_id, 45.00, 'Weekly groceries', today - timedelta(days=2), category_ids['Food']),

        # Transport expenses
        (user_id, 40.00, 'Gas refill', today - timedelta(days=1), category_ids['Transport']),
        (user_id, 25.00, 'Public transit pass', today - timedelta(days=5), category_ids['Transport']),

        # Shopping expenses
        (user_id, 65.00, 'New clothes', today - timedelta(days=3), category_ids['Shopping']),
        (user_id, 32.99, 'Online book purchase', today - timedelta(days=7), category_ids['Shopping']),

        # Bills expenses
        (user_id, 85.00, 'Electricity bill', today - timedelta(days=4), category_ids['Bills']),
        (user_id, 65.00, 'Internet bill', today - timedelta(days=6), category_ids['Bills']),

        # Entertainment expenses
        (user_id, 15.00, 'Movie ticket', today - timedelta(days=1), category_ids['Entertainment']),
        (user_id, 45.00, 'Concert tickets', today - timedelta(days=8), category_ids['Entertainment']),
    ]

    for expense in expenses_data:
        cursor.execute('''
            INSERT INTO expenses (user_id, amount, description, date, category_id)
            VALUES (?, ?, ?, ?, ?)
        ''', expense)

    db.commit()