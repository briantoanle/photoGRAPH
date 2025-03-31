from flask import Blueprint, request, jsonify, session
#from db import connection
from datetime import datetime, timezone
import bcrypt
import re
import os

# Create a Blueprint for user routes
user_routes = Blueprint("user", __name__)
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "supersecretkey")

# GET ALL USERS
@user_routes.route("/", methods=["GET"])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, first_name, last_name, email FROM users;")
            users = cursor.fetchall()
            return jsonify([
                {"user_id": u[0], "first_name": u[1], "last_name": u[2], "email": u[3]} for u in users
            ])
    finally:
        close_db_connection(conn)
# GET USER BY ID
@user_routes.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT first_name, last_name, email FROM users WHERE user_id = %s;", (user_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({"first_name": user[0], "last_name": user[1], "email": user[2]})
            else:
                return jsonify({"error": "User not found"}), 404
    finally:
        close_db_connection(conn)

# REGISTER USER
@user_routes.route("/register", methods=["POST"])
def create_user():
    data = request.json

    # Validate required fields
    required_fields = ["first_name", "last_name", "email", "password"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    first_name = data["first_name"].strip()
    last_name = data["last_name"].strip()
    email = data["email"].strip()
    password = data["password"].strip()

    # Validate email format
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email format"}), 400

    # Validate password length
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    # Hash password for security
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE email = %s;", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email already exists"}), 409

            # Insert new user into the database
            cursor.execute(
                """
                INSERT INTO users (first_name, last_name, email, password_hash)
                VALUES (%s, %s, %s, %s) RETURNING user_id;
                """,
                (first_name, last_name, email, hashed_password)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
    finally:
        close_db_connection(conn)

    return jsonify({"message": "User created successfully", "user_id": user_id}), 201
from db import get_db_connection, close_db_connection
@user_routes.route("/login", methods=["POST"])
def login_user():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    # Validate input
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, password_hash FROM users WHERE email = %s;", (email,))
            user = cursor.fetchone()

            if not user:
                return jsonify({"error": "Invalid email or password"}), 401

            user_id, stored_password = user
            if not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                return jsonify({"error": "Invalid email or password"}), 401

            # Update last login timestamp
            cursor.execute("UPDATE users SET last_login = %s WHERE user_id = %s;",
                           (datetime.now(timezone.utc), user_id))
            conn.commit()

            # Store user session using cookies
            session["user_id"] = user_id
    finally:
        close_db_connection(conn)

    return jsonify({"message": "Login successful", "user_id": user_id})

@user_routes.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id", None)
    return jsonify({"message": "Logout successful"})

@user_routes.route("/me", methods=["GET"])
def get_current_user():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"user_id": session["user_id"]})

