import MySQLdb
from algorithm import generate_timetable, validate_hard_constraints
import random

# Database connection
db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="",
    db="university_db"
)
cursor = db.cursor(MySQLdb.cursors.DictCursor)

# Fetch courses from database and transform to expected format
cursor.execute("""
    SELECT courses.course_name, courses.course_unit, courses.num_of_students, 
           CONCAT(lecturers.title, ' ', lecturers.lecture_firstname, ' ', lecturers.lecture_lastname) AS lecturer,
           courses.level, courses.course_status
    FROM courses
    LEFT JOIN lecturers ON courses.lecture_id = lecturers.lecture_id
""")
courses_db = cursor.fetchall()

courses = []
for c in courses_db:
    courses.append({
        'course_name': c['course_name'],
        'course_unit': c['course_unit'],
        'num_of_students': c['num_of_students'],
        'lecturer': c['lecturer'],
        'level': c['level'],
        'course_status': c['course_status']
    })

# Fetch rooms from database and transform to expected format
cursor.execute("""
    SELECT venue_name AS name, venue_size AS capacity
    FROM venue
""")
rooms_db = cursor.fetchall()

rooms = []
for r in rooms_db:
    rooms.append({
        'name': r['name'],
        'capacity': r['capacity']
    })

# Generate time slots as list of dicts with 'day' and 'start' keys
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
hours = [
    "08:00", "09:00", "10:00", "11:00",
    "12:00", "13:00", "14:00", "15:00",
    "16:00", "17:00", "18:00"
]
time_slots = []
for day in days:
    for hour in hours:
        time_slots.append({'day': day, 'start': hour})

cursor.close()
db.close()

# Run the timetable generation
timetable = generate_timetable(courses, rooms, time_slots, validate_hard_constraints)

# Print the generated timetable
print("\nGenerated Timetable:")
for entry in timetable:
    print(f"{entry['course_name']} ({entry['course_unit']} units) - {entry['time_slot']['day']} {entry['time_slot']['start']} in {entry['venue']} (Level: {entry['level']}, Lecturer: {entry['lecturer']})")
