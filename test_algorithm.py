import algorithm
import random

# Sample test data
courses = [
    {'course_name': 'Math 101', 'course_unit': 2, 'num_of_students': 50, 
     'lecturer': 'Dr. Smith', 'level': 100, 'course_status': 'Core'},
    {'course_name': 'CS 201', 'course_unit': 3, 'num_of_students': 30,
     'lecturer': 'Prof. Johnson', 'level': 200, 'course_status': 'Core'},
    {'course_name': 'History 101', 'course_unit': 2, 'num_of_students': 40,
     'lecturer': 'Dr. Brown', 'level': 100, 'course_status': 'Elective'}
]

rooms = [
    {'name': 'Hall A', 'capacity': 60},
    {'name': 'Hall B', 'capacity': 40},
    {'name': 'Room 101', 'capacity': 30}
]

time_slots = [
    {'day': 'Monday', 'start': '08:00', 'end': '10:00'},
    {'day': 'Monday', 'start': '10:00', 'end': '11:00'},
    {'day': 'Monday', 'start': '11:00', 'end': '12:00'},
    {'day': 'Monday', 'start': '12:00', 'end': '13:00'},  # Break time
    {'day': 'Monday', 'start': '13:00', 'end': '14:00'},
    {'day': 'Tuesday', 'start': '09:00', 'end': '10:00'},
    {'day': 'Tuesday', 'start': '10:00', 'end': '11:00'},
    {'day': 'Tuesday', 'start': '11:00', 'end': '12:00'},
    {'day': 'Tuesday', 'start': '12:00', 'end': '13:00'},  # Break time
    {'day': 'Tuesday', 'start': '13:00', 'end': '14:00'}
]

# Generate timetable
timetable = algorithm.generate_timetable(courses, rooms, time_slots, algorithm.validate_hard_constraints)

# Print results
print("\nGenerated Timetable:")
for entry in timetable:
    print(f"{entry['course_name']} ({entry['course_unit']} units) - {entry['time_slot']['day']} {entry['time_slot']['start']}-{entry['time_slot']['end']} in {entry['venue']} (Level: {entry['level']}, Lecturer: {entry['lecturer']})")

# Verify constraints
print("\nConstraint Verification:")
# 1. Check no scheduling during break time
break_time_scheduled = any(entry['time_slot']['start'] == '12:00' for entry in timetable)
print(f"No classes during break time: {'PASS' if not break_time_scheduled else 'FAIL'}")

# 2. Check 3-unit courses are split correctly
cs201_slots = [entry for entry in timetable if entry['course_name'] == 'CS 201']
print(f"3-unit course split correctly: {'PASS' if len(cs201_slots) == 2 else 'FAIL'} (found {len(cs201_slots)} slots)")

# 3. Check same level courses not at same time
level_conflicts = False
for slot in time_slots:
    if slot['start'] == '12:00':
        continue  # Skip break time
    level_courses = [entry['level'] for entry in timetable if entry['time_slot'] == slot]
    if len(level_courses) != len(set(level_courses)):
        level_conflicts = True
        break
print(f"No same-level conflicts: {'PASS' if not level_conflicts else 'FAIL'}")

# 4. Check lecturer not in two places at once
lecturer_conflicts = False
for slot in time_slots:
    if slot['start'] == '12:00':
        continue
    lecturers = [entry['lecturer'] for entry in timetable if entry['time_slot'] == slot]
    if len(lecturers) != len(set(lecturers)):
        lecturer_conflicts = True
        break
print(f"No lecturer conflicts: {'PASS' if not lecturer_conflicts else 'FAIL'}")
