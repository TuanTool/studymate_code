import sqlite3

DB = "studymate.db"

def get_connection():
    return sqlite3.connect(DB)

def init_db():
    con = get_connection()
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS course (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        teacher_id INTEGER)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS assignment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        due_date TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS submission (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER,
        student_id INTEGER,
        file_url TEXT,
        grade REAL,
        feedback TEXT)''')

    con.commit()
    con.close()
