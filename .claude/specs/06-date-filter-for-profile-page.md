---
# Spec: Date Filter for Profile Page

## Overview
This feature adds date filtering capability to the profile page in the Spendly expense tracker. Users will be able to specify a start and end date to filter their transactions, summary statistics, and category breakdown. This enhances the profile page by allowing users to analyze their spending over specific time periods, which is a common requirement in personal finance applications.

## Depends on
- Step 5: Backend routes for profile page (05-backend-routes-for-profile-page) - Requires the profile page to be implemented and displaying user data, transactions, and category breakdown.

## Routes
No new routes are required. The existing profile route (`GET /profile`) will be modified to accept optional query parameters for date filtering.

## Database changes
No database schema changes are required. The existing `expenses` table already includes a `date` column of type DATE. However, we will need to modify the query functions in `database/queries.py` to accept optional date range parameters.

## Templates
- **Create:** None
- **Modify:**
  - `templates/profile.html` - Add a date filter form above the stats and transaction sections, and update the display to show filtered data.

## Files to change
- `app.py` - Modify the `/profile` route to accept `start_date` and `end_date` query parameters and pass them to the database query functions.
- `database/queries.py` - Modify `get_user_recent_transactions`, `get_user_category_breakdown`, and `get_user_summary_stats` to accept optional `start_date` and `end_date` parameters and filter results accordingly.
- `templates/profile.html` - Add date filter form and update the display of transactions, stats, and category breakdown to reflect filtered data.

## Files to create
- None

## New dependencies
No new dependencies required. Will use:
- flask (already installed)
- sqlite3 (standard library)
- werkzeug.security (already installed for password hashing in other parts of the app)

## Rules for implementation
- No SQLAlchemy or ORMs - use raw SQLite3 with parameterized queries
- All database queries must use parameterized queries (no string formatting)
- Dates must be handled in YYYY-MM-DD format consistently with the existing schema
- When no date parameters are provided, the functions should return all data (current behavior) to maintain backward compatibility
- The date range validation (start_date <= end_date) and handle invalid dates gracefully by ignoring the filter or showing all data
- Follow existing code style in app.py and database/db.py
- Use CSS variables for styling (already defined in base.css or similar for any new styling (though no new styling is strictly required as we are modifying existing template)
- All templates extend base.html (already the case)

## Definition of done
A user can successfully:
1. Navigate to /profile and see the profile page with date filter form
2. Enter a valid start date and end date in YYYY-MM-DD format and submit the form
3. See the transactions, summary statistics, and category breakdown update to reflect only expenses within the specified date range
4. Clear the date filter (by removing the dates or submitting empty form) to see all data again
5. See appropriate handling of invalid date formats (e.g., show all data or ignore invalid input)
6. All database operations use parameterized queries
7. The profile page continues to work correctly when no date filter is applied (showing all data)