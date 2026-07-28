from flask import Flask, render_template, request, redirect, url_for, session
from database.db import get_db, init_db, seed_db
from database.queries import (
    get_user_by_id,
    get_user_summary_stats,
    get_user_recent_transactions,
    get_user_category_breakdown,
    get_user_monthly_trend
)
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
            user_id = cursor.lastrowid
            # Insert default categories for the new user
            default_categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Education', 'Other']
            for category_name in default_categories:
                cursor.execute(
                    "INSERT INTO categories (name, user_id) VALUES (?, ?)",
                    (category_name, user_id)
                )
            db.commit()
            # Set user session
            session['user_id'] = user_id
            session['user_name'] = name
            # Redirect to profile page on success
            return redirect(url_for("profile"))
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
                # Redirect to profile page on success
                return redirect(url_for("profile"))
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

    # Get date filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get summary statistics
    stats = get_user_summary_stats(user_id, start_date=start_date, end_date=end_date)

    # Get recent transactions (limit to 5 for display)
    transactions = get_user_recent_transactions(user_id, limit=5, start_date=start_date, end_date=end_date)

    # Get category breakdown
    categories = get_user_category_breakdown(user_id, start_date=start_date, end_date=end_date)

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


@app.route("/analytics")
def analytics():
    # Authentication check
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    # optional date filters from request.args (start_date, end_date)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get summary statistics
    stats = get_user_summary_stats(user_id, start_date=start_date, end_date=end_date)
    # Get category breakdown
    categories = get_user_category_breakdown(user_id, start_date=start_date, end_date=end_date)
    # Get monthly trend (last 6 months)
    monthly = get_user_monthly_trend(user_id, start_date=start_date, end_date=end_date)

    # Prepare data for template
    total_expense = stats.get('total_spent', 0)
    transaction_count = stats.get('transaction_count', 0)
    avg_transaction = (total_expense / transaction_count) if transaction_count > 0 else 0
    top_category = categories[0]['category'] if categories else '—'

    monthly_labels = [item['month'] for item in monthly]  # e.g., ['Jan', 'Feb', ...]
    monthly_data   = [item['amount'] for item in monthly]
    category_labels = [item['category'] for item in categories]
    category_data   = [item['amount'] for item in categories]

    return render_template('analytics.html',
                           total_expense=total_expense,
                           txn_count=transaction_count, 
                           avg_transaction=avg_transaction,
                           top_category=top_category,
                           monthly_labels=monthly_labels,
                           monthly_data=monthly_data,
                           category_labels=category_labels,
                           category_data=category_data)


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    # Authentication check
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        # Get form data
        amount = request.form.get("amount")
        description = request.form.get("description", "").strip()
        date = request.form.get("date")
        category_id = request.form.get("category_id")

        # Validate input
        error = None

        if not amount:
            error = "Amount is required"
        else:
            try:
                amount_float = float(amount)
                if amount_float <= 0:
                    error = "Amount must be greater than zero"
            except ValueError:
                error = "Amount must be a valid number"

        if not date:
            error = "Date is required"

        if not category_id:
            error = "Category is required"

        if error is None:
            try:
                # Insert expense into database
                cursor.execute(
                    "INSERT INTO expenses (user_id, amount, description, date, category_id) VALUES (?, ?, ?, ?, ?)",
                    (user_id, amount_float, description, date, category_id)
                )
                db.commit()
                db.close()

                # Redirect to profile page on success
                return redirect(url_for("profile"))
            except Exception as e:
                error = "An error occurred while saving the expense. Please try again."

        # If validation failed or database error occurred, fetch categories again for form
        cursor.execute("SELECT id, name FROM categories WHERE user_id = ? ORDER BY name", (user_id,))
        categories = cursor.fetchall()
        db.close()

        return render_template("expenses/add.html",
                             error=error,
                             categories=categories,
                             form_data={
                                 "amount": amount,
                                 "description": description,
                                 "date": date,
                                 "category_id": category_id
                             })

    # GET request - show the form
    try:
        cursor.execute("SELECT id, name FROM categories WHERE user_id = ? ORDER BY name", (user_id,))
        categories = cursor.fetchall()
    except Exception:
        categories = []
    finally:
        db.close()

    return render_template("expenses/add.html", categories=categories)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
