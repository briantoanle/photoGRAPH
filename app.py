import os
import psycopg2
from dotenv import load_dotenv

from flask import Flask, request, jsonify

CREATE_USERS_TABLE = """CREATE TABLE IF NOT EXISTS users (
                            user_id SERIAL PRIMARY KEY,
                            first_name VARCHAR(100) NOT NULL,
                            last_name VARCHAR(100) NOT NULL,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP WITH TIME ZONE
                        );"""
CREATE_USER = """INSERT INTO users (first_name, last_name, email, password_hash)
                    VALUES (%s, %s, %s, %s)
                    RETURNING user_id, first_name, last_name, email, created_at;"""

load_dotenv()
app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.get("/")
def home():
    return "hello world"

@app.get("/api/users")
def get_user1():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT first_name, last_name, email FROM users WHERE user_id = 3;")
            return cursor.fetchall()

#@app.route("/api/users/<int:user_id>", methods=["GET"])
@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT first_name, last_name, email FROM users WHERE user_id = %s;", (user_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({"first_name": user[0], "last_name": user[1], "email": user[2]})
            else:
                return jsonify({"error": "User not found"}), 404


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json  # Get JSON payload from request
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password_hash = data.get("password_hash")  # In real cases, hash the password

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password_hash) 
                VALUES (%s, %s, %s, %s) RETURNING user_id;
            """, (first_name, last_name, email, password_hash))
            user_id = cursor.fetchone()[0]

    return jsonify({"message": "User created", "user_id": user_id}), 201