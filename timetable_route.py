from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
import MySQLdb
from algorithm import generate_timetable, validate_hard_constraints, shuffle_timetable  # Import shuffle_timetable
import os
import csv
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_mysqldb import MySQL  # Import MySQL

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

timetable_bp = Blueprint('timetable_bp', __name__)
timetable_bp.config = {}
timetable_bp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

csrf = CSRFProtect()
mysql = MySQL()  # Initialize MySQL

def create_app():
    app = Flask(__name__)
    app.secret_key = 'IjE0YzBjOGFlNjgyN2JhNDU5ZDBlNzM3MGNmN2FhYTBiYmI0OTRiMzQi.aAZjmA.EpSBK7M2EcDw7EjmxVICbVxSsyw'  # Replace with a secure key
    csrf.init_app(app)  # Enable CSRF protection

    # MySQL configuration
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = ""
    app.config["MYSQL_DB"] = "university_db"

    mysql.init_app(app)  # Bind MySQL to the app
    return app

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@timetable_bp.route('/timetable', methods=['GET'])
def timetable():
    """
    Render the timetable page for the uploaded timetable.
    """
    # Retrieve the timetable from the session
    timetable = session.get('timetable')
    if not timetable:
        flash('No uploaded timetable file found. Please upload a file first.', 'warning')
        return redirect(url_for('timetable_bp.upload_timetable'))

    # Retrieve days and time slots
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    hours = [
        "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00",
        "16:00", "17:00", "18:00"
    ]

    return render_template(
        'uploaded_timetable.html',
        timetable=timetable,
        days=days,
        time_slots=hours
    )

# Define the form class
class UploadForm(FlaskForm):
    csv_file = FileField('Upload CSV', validators=[DataRequired()])
    submit = SubmitField('Upload and Generate')

@timetable_bp.route('/upload_timetable', methods=['GET', 'POST'])
def upload_timetable():
    """
    Handle the upload of a CSV file to generate and display a timetable.
    """
    form = UploadForm()  # Create an instance of the form

    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['csv_file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = timetable_bp.config.get('UPLOAD_FOLDER', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            flash('File successfully uploaded', 'success')

            # Process the uploaded file and generate the timetable
            courses = []
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    courses.append({
                        'course_name': row.get('course_name'),
                        'course_unit': int(row.get('course_unit', 0)),
                        'num_of_students': int(row.get('num_of_students', 0)),
                        'lecturer': row.get('lecturer'),
                        'level': int(row.get('level', 0)),
                        'course_status': row.get('course_status')
                    })

            # Fetch rooms from the database
            db = MySQLdb.connect(
                host="localhost",
                user="root",
                passwd="",
                db="university_db"
            )
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT venue_name AS name, venue_size AS capacity FROM venue")
            rooms_db = cursor.fetchall()
            rooms = [{'name': r['name'], 'capacity': r['capacity']} for r in rooms_db]

            # Generate time slots
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            hours = [
                "08:00", "09:00", "10:00", "11:00",
                "12:00", "13:00", "14:00", "15:00",
                "16:00", "17:00", "18:00"
            ]
            time_slots = [{'day': day, 'start': hour} for day in days for hour in hours]

            # Generate timetable using the uploaded file
            result = generate_timetable(courses, rooms, time_slots, validate_hard_constraints)

            # If the function returns a single value, assume it is the timetable entries
            if isinstance(result, list):
                timetable_entries = result
                unscheduled_entries = []  # No unscheduled entries provided
            else:
                timetable_entries, unscheduled_entries = result

            # Transform timetable entries into a structured format
            timetable = {day: {hour: [] for hour in hours} for day in days}
            for entry in timetable_entries:
                day = entry['time_slot']['day']
                start = entry['time_slot']['start']
                timetable[day][start].append({
                    'course_name': entry['course_name'],
                    'course_unit': entry['course_unit'],
                    'venue': entry['venue'],
                    'lecturer': entry['lecturer'],
                    'level': entry['level']
                })

            # Process unscheduled entries
            unscheduled_courses = [
                {
                    'name': entry['course_name'],
                    'hours': entry['course_unit'],
                    'reason': f"Could not schedule {entry['course_unit']} hour(s) for {entry['course_name']} (likely due to space, room, or time constraints)"
                }
                for entry in unscheduled_entries
            ]

            # Debugging: Print unscheduled courses
            print("Unscheduled Courses:", unscheduled_courses)

            # Save the timetable to the session
            session['timetable'] = timetable
            session['unscheduled_courses'] = unscheduled_courses

            # Render the timetable directly
            return render_template(
                'uploaded_timetable.html',
                timetable=timetable,
                days=days,
                time_slots=hours,
                unscheduled_courses=unscheduled_courses  # Pass unscheduled courses to the template
            )

        else:
            flash('Allowed file types are csv', 'danger')
            return redirect(request.url)

    return render_template('upload_timetable.html', form=form)  # Pass the form to the template

@timetable_bp.route('/edit_timetable', methods=['POST'])
def edit_timetable():
    """
    Swap two courses in the timetable.
    """
    # Retrieve the timetable from the session
    timetable = session.get('timetable')
    if not timetable:
        flash("No timetable found to edit.", "warning")
        return redirect(url_for('timetable_bp.timetable'))

    # Get the selected courses from the form
    course1_data = request.form.get('course1')
    course2_data = request.form.get('course2')

    if not course1_data or not course2_data:
        flash("Please select two courses to swap.", "danger")
        return redirect(url_for('timetable_bp.timetable'))

    # Parse the course data
    day1, hour1, course1_name = course1_data.split('|')
    day2, hour2, course2_name = course2_data.split('|')

    # Validate that the courses exist in the timetable
    course1 = None
    course2 = None

    for entry in timetable[day1][hour1]:
        if entry['course_name'] == course1_name:
            course1 = entry
            break

    for entry in timetable[day2][hour2]:
        if entry['course_name'] == course2_name:
            course2 = entry
            break

    if not course1 or not course2:
        flash("One or both selected courses could not be found.", "danger")
        return redirect(url_for('timetable_bp.timetable'))

    # Swap the courses
    timetable[day1][hour1].remove(course1)
    timetable[day2][hour2].remove(course2)
    timetable[day1][hour1].append(course2)
    timetable[day2][hour2].append(course1)

    # Save the updated timetable to the session
    session['timetable'] = timetable
    flash("Courses swapped successfully!", "success")
    return redirect(url_for('timetable_bp.timetable'))

@timetable_bp.route('/swap_timetable', methods=['POST'])
def swap_timetable():
    """
    Placeholder for swapping timetable logic.
    """
    flash("Swap Timetable functionality is not implemented yet.", "info")
    return redirect(url_for('timetable_bp.timetable'))

@timetable_bp.route('/clear', methods=['POST'])
def clear_timetable():
    if "admin" not in session:
        return redirect(url_for("login"))

    # Clear the timetable from the session
    session.pop('timetable', None)

    # Clear the timetable from the database
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

    return redirect(url_for("timetable_bp.timetable"))

@timetable_bp.route('/reshuffle', methods=['POST'])
def reshuffle_timetable():
    """
    Reshuffle the timetable by shuffling the scheduled entries and reassigning them to new time slots,
    while retaining all hard constraints (room, lecturer, level, etc).
    """
    from algorithm import validate_hard_constraints
    import random
    timetable = session.get('timetable')
    if not timetable:
        flash("No timetable found to reshuffle.", "warning")
        return redirect(url_for('timetable_bp.timetable'))

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    hours = [
        "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00",
        "16:00", "17:00", "18:00"
    ]
    time_slots = [(day, hour) for day in days for hour in hours]

    # Flatten all scheduled entries and remove them from the timetable
    all_entries = []
    for day in days:
        for hour in hours:
            # Remove all entries from the timetable and collect them
            while timetable[day][hour]:
                entry = timetable[day][hour].pop()
                entry_copy = entry.copy()
                entry_copy['time_slot'] = {'day': day, 'start': hour}
                if 'num_of_students' not in entry_copy:
                    entry_copy['num_of_students'] = entry.get('num_of_students', 0)
                all_entries.append(entry_copy)

    # Shuffle the entries
    random.shuffle(all_entries)

    # Reassign entries to time slots in order, but only if constraints are satisfied
    new_timetable = {day: {hour: [] for hour in hours} for day in days}
    used_slots = set()
    for entry in all_entries:
        assigned = False
        for day, hour in time_slots:
            if hour == "12:00":
                continue
            if (day, hour) in used_slots:
                continue
            if validate_hard_constraints(entry, {'name': entry['venue'], 'capacity': 0}, {'day': day, 'start': hour}, all_entries):
                new_timetable[day][hour].append(entry)
                used_slots.add((day, hour))
                assigned = True
                break
        if not assigned:
            # If no slot found, just append to the first available (should not happen if constraints are loose)
            for day, hour in time_slots:
                if hour == "12:00":
                    continue
                if (day, hour) not in used_slots:
                    new_timetable[day][hour].append(entry)
                    used_slots.add((day, hour))
                    break

    session['timetable'] = new_timetable
    flash("Timetable reshuffled successfully, all constraints retained!", "success")
    return redirect(url_for('timetable_bp.timetable'))

@timetable_bp.route('/edit_timetable_entry', methods=['POST'])
def edit_timetable_entry():
    """
    Edit a specific timetable entry.
    """
    day = request.form.get('day')
    hour = request.form.get('hour')
    course_name = request.form.get('course_name')
    new_venue = request.form.get('new_venue')

    timetable = session.get('timetable')
    if not timetable or day not in timetable or hour not in timetable[day]:
        flash("Invalid timetable entry.", "danger")
        return redirect(url_for('timetable_bp.timetable'))

    # Find and update the course entry
    for entry in timetable[day][hour]:
        if entry['course_name'] == course_name:
            entry['venue'] = new_venue
            flash(f"Updated venue for {course_name} to {new_venue}.", "success")
            break
    else:
        flash(f"Course {course_name} not found in the specified slot.", "danger")

    # Save the updated timetable back to the session
    session['timetable'] = timetable
    return redirect(url_for('timetable_bp.timetable'))
