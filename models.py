import MySQLdb
from flask_mysqldb import MySQL

mysql = MySQL()

# ---------- FUNCTION TO CREATE TABLES ----------
def create_hod_table():
    conn = mysql.connection
    cursor = conn.cursor()

    # Create HOD Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hod (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        )
    """)

    conn.commit()
    cursor.close()

def create_tables():
    conn = mysql.connection
    cursor = conn.cursor()

    # Create Admin Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    """)

    # Create Faculty Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT NULL
        )
    """)

    # Create Department Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS department (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            faculty_id INT NOT NULL,
            FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()

# ---------- ADMIN FUNCTIONS ----------
def insert_admin(username, password_hash):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admin (username, password_hash) VALUES (%s, %s)", (username, password_hash))
    conn.commit()
    cursor.close()

def get_admin(username):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE username = %s", [username])
    admin = cursor.fetchone()
    cursor.close()
    return admin

# ---------- HOD FUNCTIONS ----------
class Faculty:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

# ---------- DEPARTMENT CLASS ----------
class Department:
    def __init__(self, id, name, faculty_id):
        self.id = id
        self.name = name
        self.faculty_id = faculty_id

# ---------- ADMIN CLASS ----------
class Admin:
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

def insert_hod(name):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hod (name) VALUES (%s)", (name,))
    conn.commit()
    cursor.close()

def get_hods():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hod")
    hods = cursor.fetchall()
    cursor.close()
    return hods

def update_hod(hod_id, name):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("UPDATE hod SET name = %s WHERE id = %s", (name, hod_id))
    conn.commit()
    cursor.close()

def delete_hod(hod_id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hod WHERE id = %s", [hod_id])
    conn.commit()
    cursor.close()

def insert_faculty(name, description):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faculty (name, description) VALUES (%s, %s)", (name, description))
    conn.commit()
    cursor.close()

def get_faculties():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    faculties = cursor.fetchall()
    cursor.close()
    return faculties

# ---------- DEPARTMENT FUNCTIONS ----------
def insert_department(name, faculty_id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("INSERT INTO department (name, faculty_id) VALUES (%s, %s)", (name, faculty_id))
    conn.commit()
    cursor.close()

def get_departments():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT id, department.name, faculty.name FROM department JOIN faculty ON department.faculty_id = faculty.id")
    departments = cursor.fetchall()
    cursor.close()
    return departments
