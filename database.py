import sqlite3
import os

# Create database folder path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "college_system.db")

# Connect to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables

cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    department_id INTEGER,
    FOREIGN KEY(department_id) REFERENCES departments(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    admission_year INTEGER,
    current_sem INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT,
    sem_number INTEGER,
    department_id INTEGER,
    FOREIGN KEY(department_id) REFERENCES departments(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject_id INTEGER,
    internal INTEGER,
    assignment INTEGER,
    lab INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(subject_id) REFERENCES subjects(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    sem_number INTEGER,
    attendance_percent REAL,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS model_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_trained_size INTEGER,
    last_trained_date TEXT
)
""")

# Insert Departments
cursor.execute("INSERT OR IGNORE INTO departments (name) VALUES ('CSE')")
cursor.execute("INSERT OR IGNORE INTO departments (name) VALUES ('CIVIL')")

# Insert Default Admin
cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role, department_id)
VALUES ('admin', 'admin123', 'admin', NULL)
""")

conn.commit()
conn.close()

print("Database and tables created successfully!")