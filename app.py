from flask import Flask, render_template, request, redirect, url_for, session
from database.db import get_db, init_db, seed_db
from database.queries import get_user_by_id, get_user_summary_stats, get_user_recent_transactions, get_user_category_breakdown
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
# Secret key for session management
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate input
        if not name or not email or not password:
            return render_template("register.html", error="All fields are required")

        # Validate email format (basic check)
        if "@" not in email or "." not in email:
            return render_template("register.html", error="Please enter a valid email address")

        # Check password length
        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters long")

        # Hash the password
        password_hash = generate_password_hash(password)

        # Insert user into database
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            db.commit()
            # Redirect to login page on success
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            # Handle duplicate email
            return render_template("register.html", error="Email already exists")
        except Exception:
            # Handle other database errors
            return render_template("register.html", error="An error occurred. Please try again.")
        finally:
            db.close()

    # GET request - show the form
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get form data
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate input
        if not email or not password:
            return render_template("login.html", error="Email and password are required")

        # Validate email format (basic check)
        if "@" not in email or "." not in email:
            return render_template("login.html", error="Please enter a valid email address")

        # Check user in database
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT id, name, password_hash FROM users WHERE email = ?",
                (email,)
            )
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                # Login successful - set user session
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                # Redirect to landing page or next page
                return redirect(url_for("landing"))
            else:
                # Invalid credentials
                return render_template("login.html", error="Invalid email or password")
        except Exception:
            # Handle other database errors
            return render_template("login.html", error="An error occurred. Please try again.")
        finally:
            db.close()

    # GET request - show the form
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    # Clear the session
    session.clear()
    # Redirect to login page so user can log in again
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    # Authentication check
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Get user data from database
    user = get_user_by_id(user_id)
    if not user:
        # If user not found, clear session and redirect to login
        session.clear()
        return redirect(url_for('login'))

    # Format member_since date
    member_since = "Unknown"
    if user.get('created_at'):
        try:
            # Handle both string and datetime objects
            created_at = user['created_at']
            if isinstance(created_at, datetime):
                date_obj = created_at
            else:
                # Assuming it's a string, try to parse it
                date_obj = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            member_since = date_obj.strftime('%B %Y')
        except ValueError:
            try:
                # Try another common format for string dates
                if isinstance(created_at, str):
                    date_obj = datetime.strptime(created_at, '%Y-%m-%d')
                    member_since = date_obj.strftime('%B %Y')
            except ValueError:
                # If parsing fails, use a default
                member_since = "Unknown"
        except Exception:
            # If any other error occurs, use a default
            member_since = "Unknown"

    # Get summary statistics
    stats = get_user_summary_stats(user_id)

    # Get recent transactions (limit to 5 for display)
    transactions = get_user_recent_transactions(user_id, limit=5)

    # Get category breakdown
    categories = get_user_category_breakdown(user_id)

    # Prepare user data for template (matching the expected format)
    user_data = {
        'name': user['name'],
        'email': user['email'],
        'member_since': member_since
    }

    # Prepare stats for template (the template expects these fields on the user object)
    # But looking at the template, it uses user.total_expenses, user.transaction_count
    # So we need to add these to the user object
    user_data['total_expenses'] = stats['total_spent'] if stats else 0
    user_data['transaction_count'] = stats['transaction_count'] if stats else 0

    # For the top category in the stats card, we'll get it from categories
    # The template uses categories[0].category for the top category
    # So we'll make sure categories is sorted by amount descending

    return render_template('profile.html',
                         user=user_data,
                         transactions=transactions,
                         categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
