# University Timetable Management System

This project is a Flask-based web application for managing university timetables. It allows administrators to upload course data, generate and display timetables, handle unscheduled courses, and perform actions like clearing the timetable. The system is designed to respect all hard constraints (room, lecturer, level, etc.) and provides a modern, responsive user interface.

## Features

- **Upload Timetable:** Upload a CSV file containing course, lecturer, and venue data to generate a timetable.
- **Display Timetable:** View the generated timetable in a responsive, user-friendly table format.
- **Unscheduled Courses:** Clearly see which courses could not be scheduled and the reasons why.
- **Clear Timetable:** Remove all scheduled entries from the timetable.
- **Print Timetable:** Print only the timetable table for physical or PDF records.
- **Authentication:** Admin login required for timetable management.
- **Modern UI:** Responsive and visually appealing interface for both desktop and mobile.

## How It Works

1. **Upload CSV:** Admin uploads a CSV file with course, lecturer, and venue information.
2. **Timetable Generation:** The backend algorithm assigns courses to available time slots and venues, ensuring all constraints are met (e.g., no lecturer or room conflicts, room capacity, no overlapping for the same level, etc.).
3. **Display:** The timetable is displayed in a table, with days as rows and hours as columns. Break periods are clearly marked.
4. **Unscheduled Courses:** Any course that cannot be scheduled due to constraints is listed separately with the reason.
5. **Clear/Print:** Admin can clear the timetable or print the current timetable view.

## Project Structure

- `app.py` - Main Flask application entry point.
- `timetable_route.py` - Main route logic for timetable upload, display, clear, etc.
- `algorithm.py` - Timetable generation logic, constraint checking, and unscheduled course handling.
- `templates/` - HTML templates for all pages (mainly `uploaded_timetable.html` for the timetable view).
- `static/style.css` - Custom CSS for styling the UI.
- `requirements.txt` - Python dependencies.
- `uploads/` - Folder for uploaded CSV files.
- `database.sql` - SQL schema for the database (if using persistent storage).

## CSV Format

The uploaded CSV should contain columns for:
- Course Name
- Lecturer
- Level
- Number of Students
- Course Unit
- Course Status
- Venue (optional, can be assigned by the system)

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ayomidedavid/university-timetable.git
   cd university-timetable
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```sh
   python app.py
   ```
4. **Access the app:**
   Open your browser and go to `http://localhost:5000`

## Usage

- Log in as admin.
- Upload a CSV file to generate a timetable.
- View the timetable and unscheduled courses.
- Use the "Clear Timetable" button to reset.
- Use the "Print Timetable" button to print only the timetable table.

## Customization

- **Styling:** Edit `static/style.css` or the `<style>` block in `uploaded_timetable.html` for UI changes.
- **Algorithm:** Modify `algorithm.py` to change how courses are scheduled or to add new constraints.
- **Templates:** Update HTML files in `templates/` for layout or content changes.

## Notes

- The system is designed for university use but can be adapted for other institutions.
- All major features (upload, display, clear, print, unscheduled handling) are implemented and tested.
- For further improvements or new features, update the relevant Python or HTML files.

## License

This project is for educational and demonstration purposes. Please adapt and extend as needed for your institution.
