import random

def generate_timetable(courses, rooms, time_slots, hard_constraints):
    """
    Generate a timetable using a Greedy Algorithm for 4-unit, 3-unit, and 2-unit courses.

    :param courses: List of courses to schedule.
    :param rooms: List of available rooms.
    :param time_slots: List of available time slots.
    :param hard_constraints: Function to validate hard constraints.
    :return: Generated timetable.
    """
    timetable = []  # List to store the scheduled timetable
    unscheduled_entries = []  # List to store courses that could not be scheduled

    # Sort courses by course status
    courses.sort(key=lambda x: x['course_status'], reverse=True)

    for course in courses:
        required_hours = course['course_unit']

        # For 4-unit courses: schedule 2 hours on one day and 2 hours on another day
        # For 3-unit courses: schedule 2 hours on one day and 1 hour on another day
        # For 2-unit courses: schedule 2 consecutive hours on the same day
        if required_hours == 4:
            hour_blocks = [2, 2]
        elif required_hours == 3:
            hour_blocks = [2, 1]
        else:
            hour_blocks = [required_hours]

        for hours in hour_blocks:
            scheduled = False
            for time_slot in time_slots:
                # Skip break time (12:00 PM to 1:00 PM)
                if time_slot['start'] == "12:00":
                    continue

                # Ensure 3-unit courses are split across different days for 2-hour and 1-hour blocks
                if required_hours == 3 and hours == 1:
                    existing_slots = [
                        entry for entry in timetable if entry['course_name'] == course['course_name']
                    ]
                    if any(slot['time_slot']['day'] == time_slot['day'] for slot in existing_slots):
                        continue  # Skip if already scheduled on this day

                # Ensure 4-unit courses are split across different days for 2-hour and 1-hour blocks
                if required_hours == 4 and hours == 2:
                    existing_slots = [
                        entry for entry in timetable if entry['course_name'] == course['course_name']
                    ]
                    if any(slot['time_slot']['day'] == time_slot['day'] for slot in existing_slots):
                        continue  # Skip if already scheduled on this day

                for room in rooms:
                    # Check room capacity
                    if course['num_of_students'] > room['capacity']:
                        continue

                    # Check if the room is already occupied at this time slot
                    if any(entry['time_slot'] == time_slot and entry['venue'] == room['name'] for entry in timetable):
                        continue

                    # Check if the lecturer is already teaching at this time slot
                    if any(entry['time_slot'] == time_slot and entry['lecturer'] == course['lecturer'] for entry in timetable):
                        continue

                    # Check if the same level has another class at this time slot
                    if any(entry['time_slot'] == time_slot and entry['level'] == course['level'] for entry in timetable):
                        continue

                    # Check for consecutive slots if required
                    if hours > 1:
                        consecutive_slots = get_consecutive_slots(time_slots, time_slot, hours)
                        if not consecutive_slots:
                            continue

                        # Check constraints for all consecutive slots
                        if all(hard_constraints(course, room, slot, timetable) for slot in consecutive_slots):
                            # Schedule all consecutive slots
                            for slot in consecutive_slots:
                                timetable.append({
                                    'course_name': course['course_name'],
                                    'venue': room['name'],
                                    'time_slot': slot,
                                    'lecturer': course['lecturer'],
                                    'level': course['level'],
                                    'course_status': course['course_status'],
                                    'course_unit': course['course_unit']
                                })
                            scheduled = True
                            break
                    else:
                        # Single-hour scheduling
                        if hard_constraints(course, room, time_slot, timetable):
                            timetable.append({
                                'course_name': course['course_name'],
                                'venue': room['name'],
                                'time_slot': time_slot,
                                'lecturer': course['lecturer'],
                                'level': course['level'],
                                'course_status': course['course_status'],
                                'course_unit': course['course_unit']
                            })
                            scheduled = True
                            break
                if scheduled:
                    break
            if not scheduled:
                print(f"Warning: Could not schedule {hours} hour(s) for {course['course_name']}")
                unscheduled_entries.append({
                    'course_name': course['course_name'],
                    'course_unit': course['course_unit'],
                })

    return timetable, unscheduled_entries


def group_slots_by_day(slots):
    """
    Group time slots by day.
    """
    day_map = {}
    for slot in slots:
        day_map.setdefault(slot['time_slot']['day'], []).append(slot['time_slot'])
    return day_map


def get_consecutive_slots(time_slots, start_slot, hours_needed):
    """
    Get consecutive time slots starting from start_slot.
    Returns list of slots if found, None otherwise.
    """
    current_day = start_slot['day']
    current_time = start_slot['start']
    consecutive_slots = [start_slot]

    # Find next hours_needed-1 consecutive slots
    for i in range(1, hours_needed):
        next_slot = None
        # Find the next slot on the same day that starts immediately after current_time
        for slot in time_slots:
            if (slot['day'] == current_day and 
                slot['start'] > current_time and
                (next_slot is None or slot['start'] < next_slot['start'])):
                next_slot = slot

        if not next_slot:
            return None

        # Verify the next slot is exactly one hour after current_time
        current_hour = int(current_time.split(':')[0])
        next_hour = int(next_slot['start'].split(':')[0])
        if next_hour != current_hour + 1:
            return None

        consecutive_slots.append(next_slot)
        current_time = next_slot['start']

    return consecutive_slots


def validate_hard_constraints(course, room, time_slot, timetable):
    """
    Validate hard constraints for course scheduling.

    :param course: The course to schedule.
    :param room: The room being considered.
    :param time_slot: The time slot being considered.
    :param timetable: The current timetable.
    :return: True if all constraints are satisfied, False otherwise.
    """
    # Debugging: Print the current validation attempt
    print(f"Validating: Course={course['course_name']}, Room={room['name']}, Time Slot={time_slot}")

    # 1. Room availability check
    if any(entry['venue'] == room['name'] and entry['time_slot'] == time_slot for entry in timetable):
        print(f"Room conflict detected for {room['name']} at {time_slot}")
        return False

    # 2. Room capacity check
    if course['num_of_students'] > room['capacity']:
        print(f"Room {room['name']} cannot accommodate {course['num_of_students']} students.")
        return False

    # 3. Same level course conflict
    if any(entry['time_slot'] == time_slot and entry['level'] == course['level'] for entry in timetable):
        print(f"Level conflict for level {course['level']} at {time_slot}")
        return False

    # 4. Lecturer availability check
    if any(entry['time_slot'] == time_slot and 
           entry['lecturer'] == course['lecturer'] and
           entry['venue'] != room['name'] for entry in timetable):
        print(f"Lecturer {course['lecturer']} already teaching elsewhere at {time_slot}")
        return False

    # 5. Break time enforcement (12:00 PM to 1:00 PM)
    if time_slot['start'] == '12:00':
        print("Cannot schedule during break time (12:00 PM to 1:00 PM)")
        return False

    # 6. Hard constraint: 1-unit courses must be scheduled only on Wednesday 17:00-18:00
    if course['course_unit'] == 1:
        if not (time_slot['day'] == "Wednesday" and time_slot['start'] == "17:00"):
            print(f"1-unit course {course['course_name']} must be scheduled only on Wednesday 17:00-18:00")
            return False

    return True


def evaluate_soft_constraints(entry, timetable):
    """
    Evaluate soft constraints for a given timetable entry.

    :param entry: Timetable entry to evaluate.
    :param timetable: Current timetable.
    :return: List of soft constraint violations.
    """
    violations = []

    # Example soft constraint: Preferred room
    if 'preferred_room' in entry and entry['venue'] != entry['preferred_room']:
        violations.append(f"Course {entry['course_name']} is not scheduled in the preferred room.")

    # Example soft constraint: Preferred time
    if 'preferred_time' in entry and entry['time_slot'] != entry['preferred_time']:
        violations.append(f"Course {entry['course_name']} is not scheduled at the preferred time.")

    return violations


def shuffle_timetable(timetable, unscheduled_courses, rooms, time_slots, hard_constraints):
    """
    Attempt to reshuffle unscheduled courses into the timetable.

    :param timetable: The current timetable.
    :param unscheduled_courses: List of unscheduled courses.
    :param rooms: List of available rooms.
    :param time_slots: List of available time slots.
    :param hard_constraints: Function to validate hard constraints.
    :return: Updated timetable and remaining unscheduled courses.
    """
    remaining_unscheduled = []

    for course in unscheduled_courses:
        scheduled = False
        for time_slot in time_slots:
            # Skip break time (12:00 PM to 1:00 PM)
            if time_slot['start'] == "12:00":
                continue

            for room in rooms:
                # Check room capacity
                if course['num_of_students'] > room['capacity']:
                    continue

                # Check if the room is already occupied at this time slot
                if any(entry['time_slot'] == time_slot and entry['venue'] == room['name'] for entry in timetable):
                    continue

                # Check if the lecturer is already teaching at this time slot
                if any(entry['time_slot'] == time_slot and entry['lecturer'] == course['lecturer'] for entry in timetable):
                    continue

                # Check if the same level has another class at this time slot
                if any(entry['time_slot'] == time_slot and entry['level'] == course['level'] for entry in timetable):
                    continue

                # Check for consecutive slots if required
                if course['course_unit'] > 1:
                    consecutive_slots = get_consecutive_slots(time_slots, time_slot, course['course_unit'])
                    if not consecutive_slots:
                        continue

                    # Check constraints for all consecutive slots
                    if all(hard_constraints(course, room, slot, timetable) for slot in consecutive_slots):
                        # Schedule all consecutive slots
                        for slot in consecutive_slots:
                            timetable.append({
                                'course_name': course['course_name'],
                                'venue': room['name'],
                                'time_slot': slot,
                                'lecturer': course['lecturer'],
                                'level': course['level'],
                                'course_status': course['course_status'],
                                'course_unit': course['course_unit']
                            })
                        scheduled = True
                        break
                else:
                    # Single-hour scheduling
                    if hard_constraints(course, room, time_slot, timetable):
                        timetable.append({
                            'course_name': course['course_name'],
                            'venue': room['name'],
                            'time_slot': time_slot,
                            'lecturer': course['lecturer'],
                            'level': course['level'],
                            'course_status': course['course_status'],
                            'course_unit': course['course_unit']
                        })
                        scheduled = True
                        break
            if scheduled:
                break

        if not scheduled:
            remaining_unscheduled.append(course)

    return timetable, remaining_unscheduled
