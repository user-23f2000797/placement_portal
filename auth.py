from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, Admin, Student, Company

auth_bp = Blueprint('auth', __name__)

#Index Page Route
@auth_bp.route('/')
def index():
    return render_template('index.html')


#Registration Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


#Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']

        user = None

        if role == 'admin':
            user = Admin.query.filter_by(username=email).first()

        elif role == 'student':
            user = Student.query.filter_by(email=email).first()
            if user and user.is_blacklisted:
                flash("You are blacklisted by admin", "danger")
                return redirect(url_for('auth.login'))

        elif role == 'company':
            user = Company.query.filter_by(email=email).first()
            if user and user.approval_status != 'Approved':
                flash("Company not approved by admin", "danger")
                return redirect(url_for('auth.login'))

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful", "success")

            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'company':
                return redirect(url_for('company.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))

        flash("Invalid credentials", "danger")

    return render_template('login.html')


@auth_bp.route('/register/student', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            course=request.form['course'],
            institution=request.form['institution'],
            department=request.form['department'],
            year=request.form['year'],
            password=generate_password_hash(request.form['password']),
            is_blacklisted=False
        )

        db.session.add(student)
        db.session.commit()

        flash("Student registered successfully. Please login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('student/student_register.html')

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        company = Company(
            company_name=request.form['company_name'],
            email=request.form['email'],
            description=request.form['description'],
            hr_contact=request.form['hr_contact'],
            website=request.form['website'],
            password=generate_password_hash(request.form['password']),
            approval_status='Pending',
            is_blacklisted=False
        )

        db.session.add(company)
        db.session.commit()

        flash("Company registered. Await admin approval.", "info")
        return redirect(url_for('auth.login'))

    return render_template('company/company_register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for('auth.login'))