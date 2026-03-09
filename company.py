from flask import Blueprint, render_template, redirect, request, url_for, flash 
from flask_login import current_user, login_required
from models import db, Company , PlacementDrive, Application , Student
from datetime import datetime

#import student

company_bp = Blueprint('company', __name__, url_prefix='/company')

def company_required():
    return (current_user.is_authenticated and 
            current_user.get_id().startswith("Company") and 
            current_user.approval_status == 'Approved' and 
            not current_user.is_blacklisted )




#Company Dashboard
@company_bp.route('/dashboard')
@login_required
def dashboard():
    if not company_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    upcoming_drives = PlacementDrive.query.filter_by(company_id =current_user.id,status='Active').all()
    closed_drives = PlacementDrive.query.filter_by(company_id =current_user.id,status='Closed').all()

    return render_template('company/company_dashboard.html',
                           company=current_user,
                           upcoming_drives=upcoming_drives,
                           closed_drives=closed_drives)


# CRUD for Placement Drives
@company_bp.route('/drive/create',methods=['GET','POST'])
@login_required
def create_drive():
    if not company_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        drive = PlacementDrive(
            company_id=current_user.id,
            drive_name=request.form['drive_name'],
            job_title=request.form['job_title'],
            job_description=request.form['job_description'],
            eligibility=request.form['eligibility'],
            location=request.form['location'],
            salary=request.form['salary'],
            application_deadline=datetime.strptime(request.form['deadline'], "%Y-%m-%d").date(),
            
        )
        db.session.add(drive)
        db.session.commit()
        flash("Placement drive created", "success")
        return redirect(url_for('company.dashboard'))
    return render_template('company/create_drive.html')

@company_bp.route('drive/edit/<int:drive_id>',methods=['GET','POST'])
@login_required
def edit_drive(drive_id):
    if not company_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('company.dashboard'))
    if request.method == 'POST':
        drive.drive_name = request.form['drive_name']
        drive.job_title = request.form['job_title']
        drive.job_description = request.form['job_description']
        drive.eligibility = request.form['eligibility']
        drive.location = request.form['location']
        drive.salary = request.form['salary']
        drive.application_deadline = datetime.strptime(request.form['deadline'], "%Y-%m-%d").date()

        db.session.commit()
        flash("Placement drive updated", "success")
        return redirect(url_for('company.dashboard'))

    return render_template('company/edit_drive.html', drive=drive)

@company_bp.route('/drive/update_closed_drive/<int:drive_id>',methods=['GET','POST'])
@login_required
def update_closed_drive(drive_id):
    if not company_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('company.dashboard'))
    if request.method == 'POST':
        drive.drive_name = request.form['drive_name']
        drive.job_title = request.form['job_title']
        drive.job_description = request.form['job_description']
        drive.eligibility = request.form['eligibility']
        drive.location = request.form['location']
        drive.salary = request.form['salary']
        drive.application_deadline = datetime.strptime(request.form['deadline'], "%Y-%m-%d").date()
        drive.status = request.form['status']

        db.session.commit()
        flash("Placement drive updated", "success")
        return redirect(url_for('company.dashboard'))

    return render_template('company/update_closedDrive.html', drive=drive)

@company_bp.route('/drive/close/<int:drive_id>')
@login_required
def close_drive(drive_id):
    if not company_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id == current_user.id:
        drive.status = 'Closed'
        db.session.commit()
        flash("Placement drive closed", "warning")

    return redirect(url_for('company.dashboard'))

@company_bp.route('/drive/applications/<int:drive_id>')
@login_required
def view_applications(drive_id):
    drive=PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id !=current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('company.dashboard'))
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('company/applications.html', 
                           applications=applications,
                           drive=drive)

@company_bp.route('/application/student_application/<int:application_id>/<int:student_id>')
@login_required
def student_application(application_id,student_id):
    application = Application.query.get_or_404(application_id)
    student = Student.query.get_or_404(student_id)
    if application.drive.company_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('company.dashboard'))
    return render_template('company/student_profile.html', application=application, student=student)


@company_bp.route('/application/update_status/<int:id>', methods=['POST'])
@login_required
def update_application_status(id):
    application = Application.query.get_or_404(id)
    if application.drive.company_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('company.dashboard'))

    application.status = request.form['status']
    db.session.commit()

    flash("Application status updated", "success")
    return redirect(
        url_for('company.dashboard')
    )