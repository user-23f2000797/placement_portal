from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime
from models import Company, db, Student, PlacementDrive, Application 

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required():
    return (current_user.is_authenticated and 
            current_user.get_id().startswith("Student") and 
            not current_user.is_blacklisted)


@student_bp.route('/dashboard')
@login_required
def dashboard():
    if not student_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    
    company= Company.query.with_entities(Company.id, Company.company_name).filter_by(approval_status='Approved',is_blacklisted=False).all()
    applications = (
    db.session.query(
        PlacementDrive.drive_name,
        Company.company_name,
        Application.application_date
    )
    .join(Application, Application.drive_id == PlacementDrive.id)
    .join(Company, PlacementDrive.company_id == Company.id)
    .filter(
        Application.student_id == current_user.id,
        PlacementDrive.status == 'Active',
        Company.approval_status == 'Approved'
    )
    .all()
)

    return render_template('student/student_dashboard.html',
                           company=company,
                           applications=applications,
                           )

@student_bp.route('/company/<int:company_id>')
@login_required
def view_company(company_id):
    if not student_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    company = Company.query.get_or_404(company_id)
    drives = PlacementDrive.query.filter_by(company_id=company_id, status='Active').all()
    print(drives)
    return render_template('student/company_details.html', company=company, drives=drives)

@student_bp.route('/drive/<int:drive_id>')
@login_required
def view_drive(drive_id):
    if not student_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    drive = PlacementDrive.query.get_or_404(drive_id)
    company = Company.query.get(drive.company_id)
    return render_template('student/drive_details.html', drive=drive, company=company)

@student_bp.route('/apply/<int:drive_id>')
@login_required
def apply_drive(drive_id):
    if not student_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))

    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.status != 'Active':
        flash("This drive is not open for applications", "danger")
        return redirect(url_for('student.dashboard'))
    existing_application = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive_id
    ).first()

    if existing_application:
        flash("You have already applied for this drive", "warning")
        return redirect(url_for('student.dashboard'))
    application = Application(
        student_id=current_user.id,
        drive_id=drive_id,
        application_date=datetime.utcnow(),
        status='Applied'
    )
    db.session.add(application)
    db.session.commit()

    flash("Applied successfully", "success")
    return redirect(url_for('student.dashboard'))

@student_bp.route('/history')
@login_required
def placement_history():
    if not student_required():
        return redirect(url_for('auth.login'))
    applications = Application.query.filter_by(student_id=current_user.id).all()
    return render_template(
        'student/student_history.html',
        applications=applications
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not student_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))  
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.email = request.form['email']
        current_user.institution = request.form['institution']
        current_user.department = request.form['department']
        current_user.phone = request.form['phone']
        current_user.course = request.form['course']
        current_user.year = request.form['year']

        db.session.commit()
        flash("Profile updated", "success")
        return redirect(url_for('student.dashboard'))

    return render_template('student/student_profile.html', student=current_user)
