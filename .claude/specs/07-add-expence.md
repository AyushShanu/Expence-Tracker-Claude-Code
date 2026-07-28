---
# Spec: Add Expence

## Overview
This feature adds the ability for users to add new expenses to their expense tracker. Users can fill out a form with expense details including amount, description, date, and category. This is step 7 in the Spendly roadmap, building upon the existing authentication, profile, and date filtering features to provide core expense tracking functionality.

## Depends on
This feature depends on:
- 01-database setup (database schema including expenses table)
- 02-registration (user authentication system)
- 03-login-and-logout (user session management)
- 04-profile-page-design (user interface foundation)
- 05-backend-routes-for-profile-page (backend routing patterns)
- 06-date-filter-for-profile-page (date filtering concepts)

## Routes
- `GET /expenses/add` — Display the add expense form — logged-in
- `POST /expenses/add` — Process the submitted expense form and save to database — logged-in

## Database changes
No database changes. The expenses table was already created in the database setup step (01-database setup).

## Templates
- **Create:** `templates/expenses/add.html` — Form for adding new expenses
- **Modify:** 
  - `base.html` — Add navigation link to expenses section in the navbar
  - `profile.html` — Ensure recent transactions list includes newly added expenses

## Files to change
- `app.py` — Add GET and POST route handlers for /expenses/add
- `templates/base.html` — Add navigation link to expenses section
- `templates/profile.html` - Ensure it displays updated expenses list (should work automatically via existing functions)

## Files to create
- `templates/expenses/add.html` — New template for the add expense form

## New dependencies
No new dependencies. Uses existing Flask and Werkzeug packages.

## Rules for implementation
- No SQLAlchemy or ORMs - use parameterized queries only
- Passwords already handled by werkzeug in auth system (not directly relevant here but must continue to use)
- Use CSS variables from existing style.css - never hardcode hex values
- All templates must extend `base.html`
- Follow existing code patterns in app.py for route handling
- Use parameterized queries for all database operations
- Implement proper form validation and error handling
- Redirect to appropriate pages after form submission
- Check user authentication before allowing access

## Definition of done
- [ ] GET /expenses/add displays a form for adding expenses with fields for amount, description, date, and category
- [ ] Form validates that amount is a positive number and required fields are filled
- [ ] Form submission via POST /expenses/add saves the expense to the database
- [ ] After successful submission, user is redirected to profile page
- [ ] New expense appears in the recent transactions list on the profile page
- [ ] Form shows appropriate error messages for invalid input
- [ ] Only authenticated users can access the add expense form
- [ ] All database queries use parameterized statements
- [ ] Template extends base.html and uses existing CSS classes/variables
- [ ] Application runs without errors and passes manual testing