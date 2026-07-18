from flask import Flask, render_template, request, redirect, url_for
from database.db import get_db, init_db, seed_db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

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
                # Login successful - for now, redirect to a simple success page
                # In a full implementation, you would set up user session here
                return redirect(url_for("login"))  # Redirect back to login with success message
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
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


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
