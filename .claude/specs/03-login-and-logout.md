---
# Spec: Login and Logout

## Overview
This feature implements secure user authentication for the Spendly expense tracker. Users can log in with their email and password, and log out to end their session. This builds upon the user registration functionality implemented in Step 2, enabling personalized access to expense tracking features and redirect to teh dashboard. The implementation includes secure password verification using hashed credentials and session management to maintain user state across requests.

## Depends on
- Step 1: Database setup (01-database setup) - Requires functional users table with email and password_hash fields
- Step 2: User registration (02-registration.md) - Requires existing user accounts in the database

## Routes
- `POST /login` — Process login form submission — public
- `GET /logout` — Handle user logout — logged-in

Note: GET /login (display login form) already exists from the template, and POST /login is being added.

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
  - `templates/login.html` - Enhance to display login success/error messages
  - `templates/base.html` - Add conditional navigation links based on login status (optional enhancement)

## Files to change
- `app.py` - Add POST handler for /login route, implement login/logout logic, add session management
- `templates/login.html` - Optional: improve UI for displaying authentication feedback

## Files to create
- None

## New dependencies
No new dependencies required. Will use:
- flask (already installed) - for session management
- werkzeug.security (already installed) - for password hash verification
- sqlite3 (standard library)

## Rules for implementation
- No SQLAlchemy or ORMs - use raw SQLite3 with parameterized queries
- Passwords must be verified using werkzeug.security.check_password_hash (never compare hashes directly)
- Implement session-based authentication using Flask's session object
- Set secret key for session encryption (can use development key for now)
- All database queries must use parameterized queries (no string formatting)
- On successful login, redirect to intended page or landing page
- On logout, clear session and redirect to landing page
- Use flash messages for login success/error feedback
- Follow existing code style in app.py and database/db.py
- Ensure logout functionality works regardless of login state (no errors if not logged in)

## Definition of done
A user can successfully:
1. Navigate to /login and see the login form
2. Enter valid email and password for an existing account
3. Submit the form and be redirected to the landing page (or intended destination)
4. See a success message indicating successful login
5. Access protected features that require authentication (when implemented)
6. Click a logout link/button and be logged out
7. Be redirected to the landing page after logout
8. See that previously accessible protected features are now restricted
9. Attempting to log in with invalid credentials shows appropriate error message
10. All authentication-related database operations use parameterized queries
11. Passwords are never stored or transmitted in plain text
12. Session data is properly secured and cleared on logout