import algorithm
import random

def test_constraints():
    print("Testing Constraints...")

    # Shared Resources
    rooms = [{'name': 'Room 1', 'capacity': 100}]
    # Only one day available to force conflicts on that day
    time_slots = [
        {'day': 'Monday', 'start': '08:00', 'end': '09:00'},
        {'day': 'Monday', 'start': '09:00', 'end': '10:00'},
        {'day': 'Monday', 'start': '10:00', 'end': '11:00'},
        {'day': 'Monday', 'start': '11:00', 'end': '12:00'},
        {'day': 'Monday', 'start': '13:00', 'end': '14:00'},
        {'day': 'Monday', 'start': '14:00', 'end': '15:00'},
    ]

    # --- Test 1: Max 3 courses per day per level ---
    print("\n--- Test 1: Max 3 courses per day per level ---")
    level_courses = [
        {'course_name': 'Course A', 'course_unit': 2, 'num_of_students': 10, 'lecturer': 'L1', 'level': 100, 'course_status': 'Core'},
        {'course_name': 'Course B', 'course_unit': 2, 'num_of_students': 10, 'lecturer': 'L2', 'level': 100, 'course_status': 'Core'},
        {'course_name': 'Course C', 'course_unit': 2, 'num_of_students': 10, 'lecturer': 'L3', 'level': 100, 'course_status': 'Core'},
        {'course_name': 'Course D', 'course_unit': 2, 'num_of_students': 10, 'lecturer': 'L4', 'level': 100, 'course_status': 'Core'},
    ]
    
    # We expect A, B, C to be scheduled, and D to fail (or be unscheduled) because it would be the 4th course.
    # Note: L1, L2, L3, L4 are different lecturers to avoid lecturer constraints.
    
    timetable, unscheduled = algorithm.generate_timetable(level_courses, rooms, time_slots, algorithm.validate_hard_constraints)
    
    scheduled_courses = [entry['course_name'] for entry in timetable]
    print(f"Scheduled courses: {scheduled_courses}")
    
    unique_courses_scheduled = set(scheduled_courses)
    if len(unique_courses_scheduled) == 3:
         print("PASS: Only 3 courses scheduled for Level 100.")
    else:
         print(f"FAIL: Scheduled {len(unique_courses_scheduled)} courses. Unscheduled: {len(unscheduled)}")


    # --- Test 2: Max 2 lectures per day per lecturer ---
    print("\n--- Test 2: Max 2 lectures per day per lecturer ---")
    lecturer_courses = [
        {'course_name': 'Course X', 'course_unit': 2, 'num_of_students': 10, 'lecturer': 'Prof. Zeus', 'level': 200, 'course_status': 'Core'},
        {'course_name': 'Course Y', 'course_unit': 2, 'num_of_students': 10, 'lecturer': 'Prof. Zeus', 'level': 300, 'course_status': 'Core'},
        {'course_name': 'Course Z', 'course_unit': 2, 'num_of_students': 10, 'lecturer': 'Prof. Zeus', 'level': 400, 'course_status': 'Core'},
    ]
    
    # We expect X, Y to be scheduled, and Z to fail because it would be the 3rd course for Prof. Zeus.
    # Levels are different to avoid level constraints.
    
    timetable, unscheduled = algorithm.generate_timetable(lecturer_courses, rooms, time_slots, algorithm.validate_hard_constraints)
    
    scheduled_courses = [entry['course_name'] for entry in timetable]
    print(f"Scheduled courses: {scheduled_courses}")
    
    unique_courses_scheduled = set(scheduled_courses)
    if len(unique_courses_scheduled) == 2 and len(unscheduled) == 1:
         print("PASS: Only 2 courses scheduled for Prof. Zeus.")
    else:
         print(f"FAIL: Scheduled {len(unique_courses_scheduled)} courses. Unscheduled: {len(unscheduled)}")

if __name__ == "__main__":
    test_constraints()
