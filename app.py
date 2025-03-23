from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ✅ Set a fixed secret key (change this to a secure string)
app.secret_key = "your_super_secret_key_123"

# ✅ Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirects users who are not logged in


# Sample users list (Replace this with a database in a real application)
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25, "address": "123 Main St"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 30, "address": "456 Elm St"},
]

@app.route("/view_users")
def view_users():
    return render_template("view_users.html", users=users)

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = next((user for user in users if user["id"] == user_id), None)
    if not user:
        return "User not found", 404

    if request.method == "POST":
        user["name"] = request.form["name"]
        user["email"] = request.form["email"]
        user["age"] = request.form["age"]
        user["address"] = request.form["address"]
        return redirect(url_for("view_users"))

    return render_template("edit_user.html", user=user)

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    return f"Deleted user {user_id}"


# ✅ User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@app.route("/")
def home():
    return render_template("index.html")



# ✅ User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return User(user[0], user[1], user[2])
    return None

# ✅ Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        hashed_password = generate_password_hash(password)  # Hash the password
        
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("Username already taken. Try another one.", "danger")
            return redirect(url_for("register"))

        # Insert new user
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ✅ Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # Verify hashed password
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)  # Log the user in
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Try again.", "danger")

    return render_template("login.html")

# ✅ Dashboard (Requires Login)
@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome, {current_user.username}! <a href='/logout'>Logout</a>"

# ✅ Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

