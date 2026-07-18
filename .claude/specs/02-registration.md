---
# Spec: Registration

## Overview
This feature implements user registration functionality for the Spendly expense tracker. Users can create an account by providing their name, email, and password. The system will validate the input, hash the password for security, and store the user information in the database. This is a core feature that enables personalized expense tracking and is required before implementing login functionality.On success the user is shown with the successfull message.Then redirect to the login page.This is the entry point for all authenticated feature that follow.

## Depends on
- Step 1: Database setup (01-database setup) - Requires functional users table with proper schema

## Routes
- `POST /register` — Handle user registration form submission — public
- `GET /register` — Display registration form — public (already exists)

## Database changes
No database changes required. The existing users table schema is sufficient:
- id INTEGER PRIMARY KEY AUTOINCREMENT
- name TEXT NOT NULL
- email TEXT NOT NULL UNIQUE
- password_hash TEXT NOT NULL
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Templates
- **Create:** None
- **Modify:** 
  - `templates/register.csr` - Add server-side validation error display (optional enhancement)

## Files to change
- `app.py` - Add POST handler to /register route, implement registration logic
- `templates/register.html` - Optional: Add error display improvements

## Files to create
- None

## New dependencies
No new dependencies required. Will use:
- flask (already installed)
- werkzeug.security (already installed for password hashing)
- sqlite3 (standard library)

## Rules for implementation
- No SQLAlchemy or ORMs - use raw SQLite3 with parameterized queries
- Passwords must be hashed using werkzeug.security.generate_password_hash
- Use CSRF protection (Flask-WTF not required but can implement basic token validation if desired)
- All database queries must use parameterized queries (no string formatting)
- Validate input: name, email format, password strength (minimum 8 characters)
- Check for existing email before inserting to avoid integrity errors
- Provide clear error messages to user for invalid input or duplicate email
- On successful registration, redirect to login page with success message
- Follow existing code style in app.py and database/db.py

## Definition of done
A user can successfully:
1. Navigate to /register and see the registration form
2. Fill in valid name, email, and password (min 8 chars)
3. Submit the form and be redirected to login page
4. See a success message indicating account was created
5. Login with the newly created credentials (when login is implemented)

Validation requirements:
- Attempting to register with an existing email shows appropriate error
- Submitting form with missing fields shows validation errors
- Submitting form with invalid email format shows error
- Submitting form with password < 8 characters shows error
- All database operations use parameterized queries
- Passwords are stored as hashes, never plain text
- Application handles database errors gracefully