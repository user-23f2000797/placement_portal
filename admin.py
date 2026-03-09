#import modules
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user,login_required
from models import db, Admin, Student, Company , Application, PlacementDrive

#admin blueprint
admin_bp= Blueprint('admin', __name__,url_prefix='/admin')

#Check if user is admin
def admin_required():
    result = current_user.is_authenticated and current_user.get_id().startswith("Admin")
    print(f"admin_required check: authenticated={current_user.is_authenticated}, id={current_user.get_id() if current_user.is_authenticated else 'N/A'}, result={result}")
    return result

#Admin Dashboard
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not admin_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    students = Student.query.filter_by(is_blacklisted=False).all()
    companies = Company.query.filter_by(is_blacklisted=False, approval_status='Approved').all()
    drives = PlacementDrive.query.filter_by(status='Active').all()
    student_applications = Application.query.all()
    application_company=Company.query.filter_by(approval_status='Pending').all()

    return render_template('admin/admin_dashboard.html',
        students=students,
        companies=companies,
        drives=drives,
        student_applications=student_applications,
        application_company=application_company
    )


@admin_bp.route('/dashboard/search', methods=['GET','POST'])
@login_required
def search_dashboard():
    if not admin_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))

    search_query = request.form.get('search', '').strip()
    print("Search query:", search_query)
    students = []
    companies = []
    drives = []
    if search_query:
        companies = Company.query.filter(Company.company_name.ilike(f"%{search_query}%")).all()
        print(companies)
        students = Student.query.filter(Student.name.ilike(f"%{search_query}%")).all()
        print(students)
        drives = PlacementDrive.query.filter(PlacementDrive.drive_name.ilike(f"%{search_query}%")).all()
        print(drives)
    return render_template('admin/search_results.html',
                         students=students,
                         companies=companies,
                         drives=drives,
                         query=search_query)

#List Companies
@admin_bp.route('/companies')
@login_required
def manage_companies():
    if not admin_required():
        flash("Access denied", "danger")
        return redirect(url_for('auth.login'))
    companies = Company.query.all()
    return render_template('admin/companies.html', companies=companies)

#Approve Company
@admin_bp.route('/company/approve/<int:id>')
@login_required
def approve_company(id):
    company = db.session.get(Company, id)
    if not company:
        flash("Company not found", "danger")
        return redirect(url_for('admin.manage_companies'))
    company.approval_status = 'Approved'
    db.session.commit()

    flash("Company approved successfully", "success")
    return redirect(url_for('admin.dashboard'))

#Reject Company
@admin_bp.route('/company/reject/<int:id>')
@login_required
def reject_company(id):
    company = db.session.get(Company, id)
    if not company:
        flash("Company not found", "danger")
        return redirect(url_for('admin.manage_companies'))
    company.approval_status = 'Rejected'
    db.session.commit()

    flash("Company rejected", "danger")
    return redirect(url_for('admin.manage_companies'))

#List of Drives
@admin_bp.route('/drives/<int:id>')
@login_required
def view_drive(id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    drives = PlacementDrive.query.get(id)
    return render_template('admin/drives.html', drive=drives)

#Close Drive
@admin_bp.route('/drive/close/<int:id>')
@login_required
def close_drive(id):
    drive = db.session.get(PlacementDrive, id)
    if not drive:
        flash("Drive not found", "danger")
        return redirect(url_for('admin.view_drives'))
    drive.status = 'Closed'
    db.session.commit()

    flash("Placement drive closed", "success")
    return redirect(url_for('admin.dashboard'))


#List of Students
@admin_bp.route('/students')
@login_required
def view_students():
    if not admin_required():
        return redirect(url_for('auth.login'))

    students = Student.query.all()
    return render_template('admin/students.html', students=students)

#Student Application
@admin_bp.route('/student_applications/<int:id>')
@login_required
def view_student_applications(id):
    if not admin_required():
        return redirect(url_for('auth.login'))
    applications = Application.query.filter_by(drive_id=id).first()
    return render_template('admin/student_applications.html',applications=applications)

#Blacklist Student
@admin_bp.route('/student/blacklist/<int:id>')
@login_required
def blacklist_student(id):
    student = db.session.get(Student, id)
    if not student:
        flash("Student not found", "danger")
        return redirect(url_for('admin.view_students'))
    student.is_blacklisted = True
    db.session.commit()

    flash("Student blacklisted", "warning")
    return redirect(url_for('admin.dashboard'))

#Blacklist Company
@admin_bp.route('/company/blacklist/<int:id>')
@login_required
def blacklist_company(id):
    company = db.session.get(Company, id)
    if not company:
        flash("Company not found", "danger")
        return redirect(url_for('admin.dashboard'))
    company.is_blacklisted = True
    db.session.commit()

    flash("Company blacklisted", "warning")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/statistics')
@login_required
def statistics():
    stats = {
    "students": Student.query.filter_by(is_blacklisted=False).count(),
    "companies": Company.query.filter_by(is_blacklisted=False).count(),
    "drives": PlacementDrive.query.count(),
    "applications": Application.query.count(),

    "selected": Application.query.filter_by(status="Selected").count(),
    "rejected": Application.query.filter_by(status="Rejected").count(),
    "pending": Application.query.filter_by(status="waiting").count()
}


    return render_template(
        "admin/stat.html",
        stats=stats,
    )