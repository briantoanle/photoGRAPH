from flask import Blueprint, request, jsonify,session
from db import get_db_connection, close_db_connection
project_routes = Blueprint("projects", __name__)

# get existing projects -> return project name, model used, size of data set
# create new project

@project_routes.route("/getall", methods=["GET"])
def get_all_projects():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, project_id, project_name FROM projects;")
            projects = cursor.fetchall()
            return jsonify([
                {"user": p[0], "project_id": p[1], "project_name": p[2]}
                for p in projects
            ])
    finally:
        close_db_connection(conn)
    
@project_routes.route("/getProject/<int:project_id>", methods=["GET"])
def get_project(project_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, project_id, project_name FROM projects WHERE project_id = %s;", (project_id,))
            project = cursor.fetchone()
            return jsonify({"user_id": project[0], "project_id": project[1], "project_name": project[2]})
    
    finally:
        close_db_connection(conn)
    
@project_routes.route("/create", methods=["POST"])
def create_project():
    data = request.json
    project_name = data.get("project_name", "").strip()
    description = data.get("description", "").strip()
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if not project_name:
        return jsonify({"error": "Project name is required"}), 400

    if len(description) > 2000:
        return jsonify({"error": "Description is too long (max 2000 characters)"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO projects (project_name, description, user_id)
                VALUES (%s, %s, %s) RETURNING project_id;
                """,
                (project_name, description, user_id)
            )
            project_id = cursor.fetchone()[0]
            conn.commit()
    finally:
        close_db_connection(conn)

    return jsonify({"message": "Project created successfully", "project_id": project_id}), 201


@project_routes.route("/", methods=["GET"])
def get_user_projects():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT project_id, project_name, description, created_at, updated_at FROM projects WHERE user_id = %s;",
                (user_id,))
            projects = cursor.fetchall()
            return jsonify([
                {"project_id": p[0], "project_name": p[1], "description": p[2], "created_at": p[3], "updated_at": p[4]}
                for p in projects
            ])
    finally:
        close_db_connection(conn)