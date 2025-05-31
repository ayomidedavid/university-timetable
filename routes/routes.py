from flask import Flask, render_template, request, redirect, url_for, flash
from models import mysql, Faculty, Department, Admin
from flask_mysqldb import MySQL

db = MySQL()

from forms import FacultyForm, DepartmentForm

from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config.from_object('config.Config')  

db.init_app(app)

# Flask-Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'  # ✅ Match login route

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))

# ---------- ADMIN LOGIN ----------
@app.route('/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

# ---------- FACULTY CRUD OPERATIONS ----------
@app.route('/faculty', methods=['GET', 'POST'])
@login_required
def faculty():
    form = FacultyForm()
    if form.validate_on_submit():
        new_faculty = Faculty(name=form.name.data, description=form.description.data)
        db.session.add(new_faculty)
        db.session.commit()
        flash('Faculty added successfully!', 'success')
        return redirect(url_for('faculty'))
    
    faculties = Faculty.query.all()
    return render_template('faculty.html', form=form, faculties=faculties)

@app.route('/faculty/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_faculty(id):
    faculty = Faculty.query.get_or_404(id)
    form = FacultyForm(obj=faculty)
    
    if form.validate_on_submit():
        faculty.name = form.name.data
        faculty.description = form.description.data
        db.session.commit()
        flash('Faculty updated successfully!', 'success')
        return redirect(url_for('faculty'))
    
    return render_template('edit_faculty.html', form=form, faculty=faculty)

@app.route('/faculty/delete/<int:id>', methods=['POST'])
@login_required
def delete_faculty(id):
    faculty = Faculty.query.get_or_404(id)
    db.session.delete(faculty)
    db.session.commit()
    flash('Faculty deleted successfully!', 'danger')
    return redirect(url_for('faculty'))

# ---------- DEPARTMENT CRUD OPERATIONS ----------
@app.route('/department', methods=['GET', 'POST'])
@login_required
def department():
    form = DepartmentForm()
    if form.validate_on_submit():
        new_department = Department(name=form.name.data, faculty_id=form.faculty_id.data)
        db.session.add(new_department)
        db.session.commit()
        flash('Department added successfully!', 'success')
        return redirect(url_for('department'))
    
    departments = Department.query.all()
    return render_template('department.html', form=form, departments=departments)

@app.route('/department/edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
def edit_department(department_id):
    department = Department.query.get_or_404(department_id)
    form = DepartmentForm(obj=department)
    
    if form.validate_on_submit():
        department.name = form.name.data
        department.faculty_id = form.faculty_id.data
        db.session.commit()
        flash('Department updated successfully!', 'success')
        return redirect(url_for('department'))
    
    return render_template('edit_department.html', form=form, department=department)

@app.route('/department/delete/<int:department_id>', methods=['POST'])
@login_required
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully!', 'danger')
    return redirect(url_for('department'))

#---------------HOD CRUD---------------------
@app.route('/hod', methods=['GET', 'POST'])
@login_required
def hod():
    if request.method == 'POST':
        form = HODForm()
        if form.validate_on_submit():
            insert_hod(form.name.data)
            flash('HOD added successfully!', 'success')
            return redirect(url_for('hod'))
    
    hods = get_hods()
    form = HODForm()
    return render_template('hod.html', form=form, hods=hods)

@app.route('/hod/edit/<int:hod_id>', methods=['GET', 'POST'])
@login_required
def edit_hod(hod_id):
    hod = get_hods().get(hod_id)
    form = HODForm(obj=hod)
    
    if form.validate_on_submit():
        update_hod(hod_id, form.name.data)
        flash('HOD updated successfully!', 'success')
        return redirect(url_for('hod'))
    
    return render_template('edit_hod.html', form=form, hod=hod)

@app.route('/hod/delete/<int:hod_id>', methods=['POST'])
@login_required
def delete_hod(hod_id):
    delete_hod(hod_id)
    flash('HOD deleted successfully!', 'danger')
    return redirect(url_for('hod'))

#------------- Venue CRUD --------------
@app.route('/venue', methods=['GET', 'POST'])
@login_required
def venue():
    form = VenueForm()  # Assuming you have a VenueForm defined
    if form.validate_on_submit():
        # Logic to handle venue submission
        flash('Venue added successfully!', 'success')
        return redirect(url_for('venue'))
    
    return render_template('venue.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
