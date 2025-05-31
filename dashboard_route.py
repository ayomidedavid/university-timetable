from flask import Blueprint, render_template, session
import MySQLdb

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """
    Render the admin dashboard with counts of faculties, departments, courses, lecturers, HODs, and venues.
    """
    try:
        # Connect to the database
        db = MySQLdb.connect(
            host="localhost",
            user="root",
            passwd="",
            db="university_db"
        )
        cursor = db.cursor()

        # Fetch counts
        cursor.execute("SELECT COUNT(*) FROM faculty")
        faculty_count = cursor.fetchone()[0]
        print(f"Faculty Count: {faculty_count}")  # Debugging log

        cursor.execute("SELECT COUNT(*) FROM department")
        department_count = cursor.fetchone()[0]
        print(f"Department Count: {department_count}")  # Debugging log

        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        print(f"Course Count: {course_count}")  # Debugging log

        cursor.execute("SELECT COUNT(*) FROM lecturers")
        lecturer_count = cursor.fetchone()[0]
        print(f"Lecturer Count: {lecturer_count}")  # Debugging log

        cursor.execute("SELECT COUNT(*) FROM hod")
        hod_count = cursor.fetchone()[0]
        print(f"HOD Count: {hod_count}")  # Debugging log

        cursor.execute("SELECT COUNT(*) FROM venue")
        venue_count = cursor.fetchone()[0]
        print(f"Venue Count: {venue_count}")  # Debugging log

    except MySQLdb.Error as e:
        print(f"Error connecting to the database: {e}")
        faculty_count = department_count = course_count = lecturer_count = hod_count = venue_count = 0
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    # Debugging: Check session variable
    print(f"Session Admin: {session.get('admin')}")

    return render_template(
        'dashboard.html',
        faculty_count=faculty_count,
        department_count=department_count,
        course_count=course_count,
        lecturer_count=lecturer_count,
        hod_count=hod_count,
        venue_count=venue_count
    )
