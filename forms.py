from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired

class HODForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    faculty_id = SelectField('Department', coerce=int, validators=[DataRequired()])  # Use SelectField for department
    submit = SubmitField('Submit')

class FacultyForm(FlaskForm):
    name = StringField('Faculty Name', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Add Faculty')

class LoginForm(FlaskForm):  # Adding the LoginForm class
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class VenueForm(FlaskForm):
    name = StringField('Venue Name', validators=[DataRequired()])
    size = IntegerField('Venue Size', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired()])
    faculty_id = SelectField('Faculty', coerce=int, validators=[DataRequired()])  # Use SelectField for faculty
    submit = SubmitField('Add Department')

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired()])
    code = StringField('Course Code', validators=[DataRequired()])
    unit = IntegerField('Course Unit', validators=[DataRequired()])
    num_of_students = IntegerField('Number of Students', default=0)
    lecturer_id = SelectField('Lecturer', coerce=int, validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    level = IntegerField('Level', validators=[DataRequired()])
    status = SelectField('Course Status', choices=[('E', 'E'), ('C', 'C')], validators=[DataRequired()])  # Dropdown with E and C
    submit = SubmitField('Submit')

class LecturerForm(FlaskForm):
    title = SelectField('Title', choices=[('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Prof', 'Prof')], validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    middlename = StringField('Middle Name')
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Lecturer')

class TimetableFilterForm(FlaskForm):
    csrf_token = HiddenField()  # Define a simple form for CSRF token

class GenerateTimetableForm(FlaskForm):
    submit = SubmitField('Generate Timetable')

from flask_wtf.file import FileField, FileAllowed, FileRequired

class UploadCSVForm(FlaskForm):
    csv_file = FileField('Upload CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload')
