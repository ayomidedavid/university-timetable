from flask import Flask, render_template, request, redirect, url_for, flash, session
from routes.routes import *

from flask_wtf.csrf import CSRFProtect  # Import CSRFProtect
from forms import FacultyForm, DepartmentForm, LoginForm, HODForm, CourseForm, LecturerForm, VenueForm, TimetableFilterForm, GenerateTimetableForm  # Import your forms

from flask_mysqldb import MySQL, MySQLdb  # Import MySQLdb for DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config  # Import your configuration
import os
from werkzeug.utils import secure_filename
import pandas as pd  # Import pandas for file processing

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

from flask_wtf.csrf import CSRFProtect

from timetable_route import timetable_bp
from dashboard_route import dashboard_bp

app = Flask(__name__)
app.register_blueprint(timetable_bp)
app.register_blueprint(dashboard_bp)
app.config['SECRET_KEY'] = Config.SECRET_KEY  # Ensure SECRET_KEY is set
csrf = CSRFProtect(app)  # Initialize CSRF protection

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "university_db"

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/hod/delete/<int:hod_id>", methods=["POST"])
def delete_hod(hod_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM hod WHERE hod_id = %s", (hod_id,))
        mysql.connection.commit()
        flash("HOD deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        flash("Failed to delete HOD. Please try again.", "danger")
    finally:
        cur.close()

    return redirect(url_for("hod"))

@app.route("/hod/edit/<int:hod_id>", methods=["GET", "POST"])
def edit_hod(hod_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    hod = get_hod_by_id(hod_id)
    form = HODForm()

    # Populate department choices
    departments = get_departments()
    form.faculty_id.choices = [(department['department_id'], department['department_name']) for department in departments]

    if form.validate_on_submit():
        hod_name = form.name.data
        department_id = form.faculty_id.data

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE hod
            SET hod_name = %s, department_id = %s
            WHERE hod_id = %s
        """, (hod_name, department_id, hod_id))
        mysql.connection.commit()
        cur.close()

        flash("HOD updated successfully!", "success")
        return redirect(url_for("hod"))

    # Pre-fill form with existing data
    form.name.data = hod[1]  # hod_name
    form.faculty_id.data = hod[2]  # department_id

    return render_template("edit_hod.html", form=form, hod_id=hod_id)

from forms import TimetableFilterForm  # Import the form

@app.route("/hod/view/<int:hod_id>", methods=["GET", "POST"])
def view_hod(hod_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    form = TimetableFilterForm()  # Create an instance of the form

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT hod.hod_id, hod.hod_name, department.department_name, department.department_id
        FROM hod
        JOIN department ON hod.department_id = department.department_id
        WHERE hod.hod_id = %s
    """, (hod_id,))
    hod = cur.fetchone()
    cur.close()

    if not hod:
        flash("HOD not found!", "danger")
        return redirect(url_for("hod"))

    # Fetch filter values from the form
    level = request.form.get("level")
    course_unit = request.form.get("course_unit")
    course_status = request.form.get("course_status")

    # Build the query dynamically based on filters
    query = """
        SELECT lecturers.lecture_id, CONCAT(lecturers.title, ' ', lecturers.lecture_firstname, ' ', lecturers.lecture_lastname) AS lecturer_name,
               courses.course_name, courses.course_code, courses.course_unit, courses.level, courses.course_status
        FROM lecturers
        LEFT JOIN courses ON lecturers.lecture_id = courses.lecture_id
        WHERE lecturers.department_id = %s
    """
    params = [hod['department_id']]

    if level:
        query += " AND courses.level = %s"
        params.append(level)
    if course_unit:
        query += " AND courses.course_unit = %s"
        params.append(course_unit)
    if course_status:
        query += " AND courses.course_status = %s"
        params.append(course_status)

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(query, params)
    lecturers_courses = cur.fetchall()
    cur.close()

    return render_template("view_hod.html", form=form, hod=hod, lecturers_courses=lecturers_courses, level=level, course_unit=course_unit, course_status=course_status)

# ========== ADMIN AUTH ROUTES ==========
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(f"Username entered: {username}")  # Debug statement

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username = %s", [username])
        admin = cur.fetchone()
        cur.close()

        if admin and check_password_hash(admin[2], password):  # Check password hash
            session["admin"] = username
            print(f"Session after login: {session}")  # Debug statement to check session contents
            flash("Login Successful", "success")

            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Username or Password", "danger")

    form = LoginForm()  # Create an instance of the login form
    return render_template("login.html", form=form)  # Pass the form to the template


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    form = GenerateTimetableForm()  # Create an instance of the form
    return render_template("dashboard.html", form=form)


@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

@app.route("/faculty", methods=["GET", "POST"])
def faculty():
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        try:
            cur.execute("INSERT INTO faculty (faculty_name, faculty_description) VALUES (%s, %s)", (name, description))
            mysql.connection.commit()
            flash("Faculty added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")  # Debug statement
            flash("Failed to add faculty. Please try again.", "danger")
    
    cur.execute("SELECT faculty_id, faculty_name, faculty_description FROM faculty")  # Specify the columns
    faculties = cur.fetchall()
    cur.close()

    form = FacultyForm()  # Create an instance of the FacultyForm
    return render_template("faculty.html", faculties=faculties, form=form)  # Pass the faculties and form to the template

@app.route("/faculty/delete/<int:id>", methods=["POST"])
def delete_faculty(id):
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM faculty WHERE faculty_id = %s", (id,))
        mysql.connection.commit()
        flash("Faculty deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        flash("Failed to delete faculty. Please try again.", "danger")
    finally:
        cur.close()

    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    cur.execute("SELECT faculty_id, faculty_name, faculty_description FROM faculty")  # Specify the columns
    faculties = cur.fetchall()
    cur.close()

    form = FacultyForm()  # Create an instance of the FacultyForm
    return render_template("faculty.html", faculties=faculties, form=form)  # Pass the faculties and form to the template

@app.route('/edit_faculty/<int:id>', methods=['POST'])
def edit_faculty(id):
    if "admin" not in session:
        return redirect(url_for("login"))

    name = request.form['name']
    description = request.form['description']

    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE faculty SET faculty_name = %s, faculty_description = %s WHERE faculty_id = %s", (name, description, id))
        mysql.connection.commit()
        flash("Faculty updated successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        flash("Failed to update faculty. Please try again.", "danger")
    finally:
        cur.close()

    return redirect(url_for('faculty'))

def get_departments():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use a dictionary cursor
    query = """
        SELECT department.department_id, department.department_name, faculty.faculty_name
        FROM department
        JOIN faculty ON department.faculty_id = faculty.faculty_id
    """
    cur.execute(query)
    departments = cur.fetchall()
    cur.close()
    return departments

def get_faculties():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use a dictionary cursor
    cur.execute("SELECT faculty_id, faculty_name FROM faculty")
    faculties = cur.fetchall()
    cur.close()
    return faculties

def get_all_hods():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use a dictionary cursor
    cur.execute("SELECT hod_id, hod_name, department_id FROM hod")
    hods = cur.fetchall()
    cur.close()
    return hods

def get_lecturers():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use a dictionary cursor
    cur.execute("""
        SELECT lecturers.lecture_id, lecturers.lecture_firstname, lecturers.lecture_lastname, lecturers.lecture_middlename, department.department_name
        FROM lecturers
        JOIN department ON lecturers.department_id = department.department_id
    """)
    lecturers = cur.fetchall()
    cur.close()
    return lecturers

def get_lecturer_by_id(lecture_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT lecture_id, lecture_firstname, lecture_middlename, lecture_lastname, department_id
        FROM lecturers
        WHERE lecture_id = %s
    """, (lecture_id,))
    lecturer = cur.fetchone()
    cur.close()
    return lecturer

@app.route('/department', methods=['GET', 'POST'])
def department():
    form = DepartmentForm()
    faculties = get_faculties()
    form.faculty_id.choices = [(faculty['faculty_id'], faculty['faculty_name']) for faculty in faculties]

    if form.validate_on_submit():
        name = form.name.data
        faculty_id = form.faculty_id.data

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO department (department_name, faculty_id) VALUES (%s, %s)", (name, faculty_id))
            mysql.connection.commit()
            flash("Department added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")  # Debug statement
            flash("Failed to add department. Please try again.", "danger")
        finally:
            cur.close()

        return redirect(url_for("department"))

    departments = get_departments()  # Fetch all departments
    return render_template("department.html", departments=departments, form=form)

@app.route("/department/delete/<int:id>", methods=["POST"])
def delete_department(id):
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM department WHERE department_id = %s", (id,))
        mysql.connection.commit()
        flash("Department deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        flash("Failed to delete department. Please try again.", "danger")
    finally:
        cur.close()

    return redirect(url_for("department"))

@app.route("/department/edit/<int:department_id>", methods=["GET", "POST"])
def edit_department(department_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use a dictionary cursor
    
    if request.method == "POST":
        name = request.form["name"]
        faculty_id = request.form["faculty_id"]
        
        cur.execute("UPDATE department SET department_name = %s, faculty_id = %s WHERE department_id = %s", (name, faculty_id, department_id))
        mysql.connection.commit()
        cur.close()
        
        flash("Department updated successfully!", "success")
        return redirect(url_for("department"))
    
    cur.execute("SELECT * FROM department WHERE department_id = %s", (department_id,))
    department = cur.fetchone()
    cur.close()

    if not department:
        flash("Department not found!", "danger")
        return redirect(url_for("department"))

    form = DepartmentForm()
    faculties = get_faculties()
    form.faculty_id.choices = [(faculty['faculty_id'], faculty['faculty_name']) for faculty in faculties]
    form.name.data = department["department_name"]  # Pre-fill the form with existing data
    form.faculty_id.data = department["faculty_id"]  # Pre-fill the faculty ID

    return render_template("edit_department.html", form=form, department_id=department_id)

@app.route("/hod", methods=["GET", "POST"])
def hod():
    if "admin" not in session:
        return redirect(url_for("login"))

    form = HODForm()
    departments = get_departments()
    form.faculty_id.choices = [(department['department_id'], department['department_name']) for department in departments]

    if form.validate_on_submit():
        hod_name = form.name.data
        department_id = form.faculty_id.data

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO hod (hod_name, department_id) VALUES (%s, %s)", (hod_name, department_id))
            mysql.connection.commit()
            flash("HOD added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")  # Debug statement
            flash("Failed to add HOD. Please try again.", "danger")
        finally:
            cur.close()

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT hod.hod_id, hod.hod_name, department.department_name
        FROM hod
        JOIN department ON hod.department_id = department.department_id
    """)
    hods = cur.fetchall()
    cur.close()

    return render_template("hod.html", hods=hods, form=form)

@app.route("/course", methods=["GET", "POST"])
def course():
    if "admin" not in session:
        return redirect(url_for("login"))

    form = CourseForm()
    lecturers = get_lecturers()
    departments = get_departments()
    form.lecturer_id.choices = [(lecturer['lecture_id'], f"{lecturer['lecture_firstname']} {lecturer['lecture_lastname']}") for lecturer in lecturers]
    form.department_id.choices = [(department['department_id'], department['department_name']) for department in departments]

    # Populate dropdown options for course unit, level, and status
    form.unit.choices = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]
    form.level.choices = [(100, "100"), (200, "200"), (300, "300"), (400, "400"), (500, "500")]
    form.status.choices = [("C", "C"), ("E", "E")]  # Ensure correct values for course status

    if form.validate_on_submit():
        course_name = form.name.data
        course_code = form.code.data
        course_unit = form.unit.data
        num_of_students = form.num_of_students.data
        lecturer_id = form.lecturer_id.data
        department_id = form.department_id.data
        level = form.level.data
        course_status = form.status.data

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO courses (course_name, course_code, course_unit, num_of_students, lecture_id, department_id, level, course_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (course_name, course_code, course_unit, num_of_students, lecturer_id, department_id, level, course_status))
            mysql.connection.commit()
            flash("Course added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")
            flash("Failed to add course. Please try again.", "danger")
        finally:
            cur.close()

    # Filtering logic
    lecturer_filter = request.args.get("lecturer")
    unit_filter = request.args.get("unit")
    level_filter = request.args.get("level")
    status_filter = request.args.get("status")
    department_filter = request.args.get("department")

    query = """
        SELECT 
            courses.course_id, 
            courses.course_name, 
            courses.course_code, 
            courses.course_unit, 
            courses.num_of_students, 
            CONCAT(lecturers.title, ' ', lecturers.lecture_firstname, ' ', lecturers.lecture_lastname) AS lecturer_name, 
            department.department_name AS department_name, 
            courses.level AS course_level, 
            courses.course_status AS course_status
        FROM courses
        JOIN lecturers ON courses.lecture_id = lecturers.lecture_id
        JOIN department ON courses.department_id = department.department_id
        WHERE 1=1
    """
    params = []

    if lecturer_filter:
        query += " AND lecturers.lecture_id = %s"
        params.append(lecturer_filter)
    if unit_filter:
        query += " AND courses.course_unit = %s"
        params.append(unit_filter)
    if level_filter:
        query += " AND courses.level = %s"
        params.append(level_filter)
    if status_filter:
        query += " AND courses.course_status = %s"
        params.append(status_filter)
    if department_filter:
        query += " AND department.department_id = %s"
        params.append(department_filter)

    cur = mysql.connection.cursor()
    cur.execute(query, params)
    courses = cur.fetchall()
    cur.close()

    return render_template("course.html", courses=courses, form=form, lecturers=lecturers, departments=departments)

@app.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    course = get_course_by_id(course_id)  # Assuming this returns a tuple
    form = CourseForm()

    # Populate lecturer and department choices
    lecturers = get_lecturers()
    departments = get_departments()
    form.lecturer_id.choices = [(lecturer['lecture_id'], f"{lecturer['lecture_firstname']} {lecturer['lecture_middlename']} {lecturer['lecture_lastname']}") for lecturer in lecturers]
    form.department_id.choices = [(department['department_id'], department['department_name']) for department in departments]

    if form.validate_on_submit():
        course_name = form.name.data
        course_code = form.code.data
        course_unit = form.unit.data
        num_of_students = form.num_of_students.data
        lecturer_id = form.lecturer_id.data
        department_id = form.department_id.data
        level = form.level.data
        course_status = form.status.data  # Handle course_status

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE courses
            SET course_name = %s, course_code = %s, course_unit = %s, num_of_students = %s, lecture_id = %s, department_id = %s, level = %s, course_status = %s
            WHERE course_id = %s
        """, (course_name, course_code, course_unit, num_of_students, lecturer_id, department_id, level, course_status, course_id))
        mysql.connection.commit()
        cur.close()

        flash("Course updated successfully!", "success")
        return redirect(url_for('course'))

    # Access tuple elements by index
    form.name.data = course[1]  # course_name
    form.code.data = course[2]  # course_code
    form.unit.data = course[3]  # course_unit
    form.num_of_students.data = course[4]  # num_of_students
    form.lecturer_id.data = course[5]  # lecture_id
    form.department_id.data = course[6]  # department_id
    form.level.data = course[7]  # level
    form.status.data = course[8]  # course_status

    return render_template('edit_course.html', form=form, course=course, course_id=course_id)

@app.route("/course/delete/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
        mysql.connection.commit()
        flash("Course deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        flash("Failed to delete course. Please try again.", "danger")
    finally:
        cur.close()

    return redirect(url_for("course"))

def get_course_by_id(course_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT course_id, course_name, course_code, course_unit, num_of_students, lecture_id, department_id, level, course_status
        FROM courses
        WHERE course_id = %s
    """, (course_id,))
    course = cur.fetchone()
    cur.close()
    return course

@app.route("/lecturer", methods=["GET", "POST"])
def lecturer():
    if "admin" not in session:
        return redirect(url_for("login"))

    form = LecturerForm()
    departments = get_departments()
    form.department_id.choices = [(department['department_id'], department['department_name']) for department in departments]

    if form.validate_on_submit():
        title = form.title.data  # Ensure the title field is retrieved from the form
        lecturer_firstname = form.firstname.data
        lecturer_lastname = form.lastname.data
        lecturer_middlename = form.middlename.data
        department_id = form.department_id.data
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO lecturers (title, lecture_firstname, lecture_lastname, lecture_middlename, department_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, lecturer_firstname, lecturer_lastname, lecturer_middlename, department_id))
            mysql.connection.commit()
            flash("Lecturer added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")  # Debug statement
            flash("Failed to add lecturer. Please try again.", "danger")
        finally:
            cur.close()

    # Filtering logic
    department_filter = request.args.get("department")

    query = """
        SELECT lecturers.lecture_id, lecturers.title, lecturers.lecture_firstname, lecturers.lecture_middlename, 
               lecturers.lecture_lastname, department.department_name
        FROM lecturers
        JOIN department ON lecturers.department_id = department.department_id
        WHERE 1=1
    """
    params = []

    if department_filter:
        query += " AND department.department_id = %s"
        params.append(department_filter)

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use a dictionary cursor
    cur.execute(query, params)
    lecturers = cur.fetchall()
    cur.close()

    return render_template("lecturer.html", lecturers=lecturers, form=form, departments=departments)  # Pass the lecturers and departments to the template

@app.route('/lecturer/edit/<int:lecture_id>', methods=['GET', 'POST'])
def edit_lecturer(lecture_id):
    lecturer = get_lecturer_by_id(lecture_id)  # Assuming this returns a tuple
    form = LecturerForm()

    # Populate department choices
    departments = get_departments()
    form.department_id.choices = [(department['department_id'], department['department_name']) for department in departments]

    if form.validate_on_submit():
        title = form.title.data
        lecturer_firstname = form.firstname.data
        lecturer_middlename = form.middlename.data
        lecturer_lastname = form.lastname.data
        department_id = form.department_id.data

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE lecturers
            SET title = %s, lecture_firstname = %s, lecture_middlename = %s, lecture_lastname = %s, department_id = %s
            WHERE lecture_id = %s
        """, (title, lecturer_firstname, lecturer_middlename, lecturer_lastname, department_id, lecture_id))
        mysql.connection.commit()
        cur.close()

        flash("Lecturer updated successfully!", "success")
        return redirect(url_for('lecturer'))

    # Access tuple elements by index
    form.title.data = lecturer[0]  # title
    form.firstname.data = lecturer[1]  # lecture_firstname
    form.middlename.data = lecturer[2]  # lecture_middlename
    form.lastname.data = lecturer[3]  # lecture_lastname
    form.department_id.data = lecturer[4]  # department_id

    return render_template('edit_lecturer.html', form=form, lecturer=lecturer, lecture_id=lecture_id)

@app.route("/lecturer/delete/<int:lecture_id>", methods=["POST"])
def delete_lecturer(lecture_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM lecturers WHERE lecture_id = %s", (lecture_id,))
        mysql.connection.commit()
        flash("Lecturer deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        flash("Failed to delete lecturer. Please try again.", "danger")
    finally:
        cur.close()

    return redirect(url_for("lecturer"))

@app.route("/venue", methods=["GET", "POST"])
def venue():
    if "admin" not in session:
        return redirect(url_for("login"))

    form = VenueForm()

    if form.validate_on_submit():
        venue_name = form.name.data
        venue_size = form.size.data
        venue_location = form.location.data
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO venue (venue_name, venue_size, venue_location) VALUES (%s, %s, %s)", 
                        (venue_name, venue_size, venue_location))
            mysql.connection.commit()
            flash("Venue added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}")  # Debug statement
            flash("Failed to add venue. Please try again.", "danger")
        finally:
            cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT venue_id, venue_name, venue_size, venue_location FROM venue")  # Specify the columns
    venues = cur.fetchall()
    cur.close()

    return render_template("venue.html", venues=venues, form=form)  # Pass the venues and form to the template

@app.route('/venue/edit/<int:venue_id>', methods=['GET', 'POST'])
def edit_venue(venue_id):
    venue = get_venue_by_id(venue_id)  # Assuming this returns a tuple
    form = VenueForm()

    if form.validate_on_submit():
        venue_name = form.name.data
        venue_size = form.size.data
        venue_location = form.location.data

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE venue
            SET venue_name = %s, venue_size = %s, venue_location = %s
            WHERE venue_id = %s
        """, (venue_name, venue_size, venue_location, venue_id))
        mysql.connection.commit()
        cur.close()

        flash("Venue updated successfully!", "success")
        return redirect(url_for('venue'))

    # Access tuple elements by index
    form.name.data = venue[1]  # venue_name
    form.size.data = venue[2]  # venue_size
    form.location.data = venue[3]  # venue_location

    return render_template('edit_venue.html', form=form, venue=venue, venue_id=venue_id)

@app.route("/venue/delete/<int:venue_id>", methods=["POST"])
def delete_venue(venue_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM venue WHERE venue_id = %s", (venue_id,))
        mysql.connection.commit()
        flash("Venue deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        flash("Failed to delete venue. Please try again.", "danger")
    finally:
        cur.close()

    return redirect(url_for("venue"))

def get_venue_by_id(venue_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT venue_id, venue_name, venue_size, venue_location
        FROM venue
        WHERE venue_id = %s
    """, (venue_id,))
    venue = cur.fetchone()
    cur.close()
    return venue

def validate_timetable(data):
    """
    Validate the timetable data against hard and soft constraints.
    :param data: DataFrame containing the timetable data
    :return: Tuple of (hard constraint errors, soft constraint warnings)
    """
    hard_errors = []
    soft_warnings = []

    # Hard Constraints
    # 1. Room Availability
    if data.duplicated(subset=['room', 'time_slot']).any():
        hard_errors.append("A room can only be used for one event at a time.")

    # 2. Teacher/Instructor Availability
    if data.duplicated(subset=['teacher', 'time_slot']).any():
        hard_errors.append("A teacher can only teach one class at a time.")

    # 3. Class Size
    if (data['class_size'] > data['room_capacity']).any():
        hard_errors.append("Class size exceeds room capacity.")

    # 4. Time Slot Availability
    if data['time_slot'].isnull().any():
        hard_errors.append("Some events are missing time slots.")

    # 5. Curriculum Requirements
    # Add specific curriculum-related validations here

    # 6. Student Scheduling Conflicts
    if data.duplicated(subset=['student', 'time_slot']).any():
        hard_errors.append("A student cannot be scheduled for two classes at the same time.")

    # Soft Constraints
    # 1. Teacher/Instructor Preferences
    if 'preferred_time' in data.columns:
        violations = data[data['time_slot'] != data['preferred_time']]
        if not violations.empty:
            soft_warnings.append(f"{len(violations)} events do not match teacher preferred times.")

    # 2. Student Preferences
    if 'student_preferred_time' in data.columns:
        violations = data[data['time_slot'] != data['student_preferred_time']]
        if not violations.empty:
            soft_warnings.append(f"{len(violations)} events do not match student preferred times.")

    # 3. Room Preferences
    if 'preferred_room' in data.columns:
        violations = data[data['room'] != data['preferred_room']]
        if not violations.empty:
            soft_warnings.append(f"{len(violations)} events do not match preferred rooms.")

    # 4. Break Distribution
    if 'break_time' in data.columns:
        breaks = data[data['time_slot'].isin(data['break_time'])]
        if breaks.empty:
            soft_warnings.append("Breaks are not evenly distributed throughout the day.")

    # 5. Travel Time
    if 'travel_time' in data.columns:
        violations = data[data['travel_time'] > 15]  # Example: Travel time > 15 minutes
        if not violations.empty:
            soft_warnings.append(f"{len(violations)} events have excessive travel time between classes.")

    # Add more soft constraints as needed...

    return hard_errors, soft_warnings

# @app.route('/model', methods=['GET', 'POST'])
# @csrf.exempt  # If CSRF protection is causing issues, you can exempt this route
# def model():
#     if "admin" not in session:
#         return redirect(url_for("login"))

#     # Remove invalid code and ensure proper logic
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cur.execute("SELECT * FROM timetable ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), time_slot")
#     timetable = cur.fetchall()
#     print("Fetched Timetable:", timetable)  # Debug statement
#     return render_template('timetable.html', timetable=timetable)

def get_hod_by_id(hod_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT hod_id, hod_name, department_id
        FROM hod
        WHERE hod_id = %s
    """, (hod_id,))
    hod = cur.fetchone()
    cur.close()
    return hod

@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    if "admin" not in session:
        return redirect(url_for("login"))

    enable_swap = request.args.get('edit', 'false') == 'true'  # Check if edit mode is enabled

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM timetable ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), time_slot")
    timetable = cur.fetchall()
    cur.close()

    return render_template('timetable.html', timetable=timetable, enable_swap=enable_swap)

@app.route('/timetable/clear', methods=['POST'])
def clear_timetable():
    if "admin" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM timetable")  # Clear all entries in the timetable table
        mysql.connection.commit()
        flash("Timetable cleared successfully!", "success")
    except Exception as e:
        print(f"Error: {e}")  # Debug statement
        flash("Failed to clear timetable. Please try again.", "danger")
    finally:
        cur.close()

    return redirect(url_for("timetable"))

from flask_wtf import FlaskForm  # Import FlaskForm
from wtforms import HiddenField  # Import HiddenField for CSRF token

if __name__ == "__main__":
    app.run(debug=True)

