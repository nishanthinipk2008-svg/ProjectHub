from flask import Flask, jsonify, request, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# =========================================
# PROJECT PATHS
# =========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
DATABASE_DIR = os.path.join(BASE_DIR, "..", "database")

DATABASE = os.path.join(DATABASE_DIR, "projecthub.db")


# =========================================
# DATABASE CONNECTION
# =========================================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =========================================
# INITIALIZE DATABASE
# =========================================

def initialize_database():

    os.makedirs(DATABASE_DIR, exist_ok=True)

    connection = get_db()

    # =====================================
    # PROJECTS TABLE
    # =====================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            manager TEXT,
            progress INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Fix old database structure
    columns = connection.execute(
        "PRAGMA table_info(projects)"
    ).fetchall()

    existing_columns = [
        column["name"] for column in columns
    ]

    if "category" not in existing_columns:
        connection.execute(
            "ALTER TABLE projects ADD COLUMN category TEXT"
        )

    if "manager" not in existing_columns:
        connection.execute(
            "ALTER TABLE projects ADD COLUMN manager TEXT"
        )

    if "progress" not in existing_columns:
        connection.execute(
            "ALTER TABLE projects ADD COLUMN progress INTEGER DEFAULT 0"
        )

    if "status" not in existing_columns:
        connection.execute(
            "ALTER TABLE projects ADD COLUMN status TEXT DEFAULT 'Pending'"
        )

    # =====================================
    # TASKS TABLE
    # =====================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            project_name TEXT,
            completed INTEGER DEFAULT 0
        )
    """)

    # =====================================
    # TEAM TABLE
    # =====================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS team (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT
        )
    """)

    # =====================================
    # DEFAULT PROJECTS
    # =====================================

    project_count = connection.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    if project_count == 0:

        connection.executemany("""
            INSERT INTO projects
            (name, category, manager, progress, status)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (
                "Smart Attendance System",
                "Web Application",
                "Arun Kumar",
                85,
                "Completed"
            ),
            (
                "Online Learning Platform",
                "Education",
                "Priya",
                65,
                "In Progress"
            ),
            (
                "Hospital Management System",
                "Healthcare",
                "Rahul",
                45,
                "Pending"
            ),
            (
                "Inventory Management",
                "Business",
                "Meena",
                72,
                "In Progress"
            )
        ])

    # =====================================
    # DEFAULT TASKS
    # =====================================

    task_count = connection.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    if task_count == 0:

        connection.executemany("""
            INSERT INTO tasks
            (task_name, project_name, completed)
            VALUES (?, ?, ?)
        """, [
            (
                "Design Dashboard UI",
                "Smart Attendance System",
                1
            ),
            (
                "Database Integration",
                "Hospital Management System",
                0
            ),
            (
                "Testing Module",
                "Online Learning Platform",
                1
            )
        ])

    # =====================================
    # DEFAULT TEAM MEMBERS
    # =====================================

    team_count = connection.execute(
        "SELECT COUNT(*) FROM team"
    ).fetchone()[0]

    if team_count == 0:

        connection.executemany("""
            INSERT INTO team
            (name, role)
            VALUES (?, ?)
        """, [
            (
                "Arun Kumar",
                "Project Manager"
            ),
            (
                "Priya",
                "Developer"
            ),
            (
                "Rahul",
                "Database Developer"
            )
        ])

    # Save everything
    connection.commit()
    connection.close()


# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# =========================================
# CSS FILE
# =========================================

@app.route("/style.css")
def style():
    return send_from_directory(
        FRONTEND_DIR,
        "style.css"
    )


# =========================================
# JAVASCRIPT FILE
# =========================================

@app.route("/script.js")
def script():
    return send_from_directory(
        FRONTEND_DIR,
        "script.js"
    )


# =========================================
# GET ALL PROJECTS
# =========================================

@app.route("/api/projects", methods=["GET"])
def get_projects():

    connection = get_db()

    projects = connection.execute("""
        SELECT *
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return jsonify([
        dict(project)
        for project in projects
    ])


# =========================================
# ADD NEW PROJECT
# =========================================

@app.route("/api/projects", methods=["POST"])
def add_project():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No project data received"
        }), 400

    name = data.get("name")
    category = data.get("category", "")
    manager = data.get("manager", "")
    progress = data.get("progress", 0)
    status = data.get("status", "Pending")

    if not name:
        return jsonify({
            "error": "Project name is required"
        }), 400

    connection = get_db()

    cursor = connection.execute("""
        INSERT INTO projects
        (name, category, manager, progress, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        category,
        manager,
        progress,
        status
    ))

    connection.commit()

    project_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Project added successfully",
        "project_id": project_id
    }), 201


# =========================================
# DELETE PROJECT
# =========================================

@app.route(
    "/api/projects/<int:project_id>",
    methods=["DELETE"]
)
def delete_project(project_id):

    connection = get_db()

    cursor = connection.execute("""
        DELETE FROM projects
        WHERE id = ?
    """, (project_id,))

    connection.commit()

    deleted = cursor.rowcount

    connection.close()

    if deleted == 0:
        return jsonify({
            "error": "Project not found"
        }), 404

    return jsonify({
        "message": "Project deleted successfully"
    })


# =========================================
# DASHBOARD STATISTICS
# =========================================

@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    connection = get_db()

    total_projects = connection.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    active_projects = connection.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE status = 'In Progress'
        """
    ).fetchone()[0]

    completed_projects = connection.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE status = 'Completed'
        """
    ).fetchone()[0]

    pending_tasks = connection.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE completed = 0
        """
    ).fetchone()[0]

    connection.close()

    return jsonify({
        "totalProjects": total_projects,
        "activeProjects": active_projects,
        "completedProjects": completed_projects,
        "pendingTasks": pending_tasks
    })


# =========================================
# GET TASKS
# =========================================

@app.route("/api/tasks", methods=["GET"])
def get_tasks():

    connection = get_db()

    tasks = connection.execute("""
        SELECT *
        FROM tasks
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return jsonify([
        dict(task)
        for task in tasks
    ])


# =========================================
# GET TEAM MEMBERS
# =========================================

@app.route("/api/team", methods=["GET"])
def get_team():

    connection = get_db()

    members = connection.execute("""
        SELECT *
        FROM team
        ORDER BY id ASC
    """).fetchall()

    connection.close()

    return jsonify([
        dict(member)
        for member in members
    ])


# =========================================
# START PROJECTHUB SERVER
# =========================================

if __name__ == "__main__":

    initialize_database()

    print("====================================")
    print("        PROJECTHUB BACKEND")
    print("====================================")
    print("Database connected successfully!")
    print("Frontend connected successfully!")
    print("Server running at:")
    print("http://127.0.0.1:5000")
    print("====================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )