from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db= SQLAlchemy()

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def get_id(self):
        return f"Admin-{self.id}"

class Student(UserMixin,db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    course = db.Column(db.String(100))
    institution = db.Column(db.String(150))
    department = db.Column(db.String(100))
    year = db.Column(db.String(20))
    password = db.Column(db.String(150), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    def get_id(self):
        return f"Student-{self.id}"

class Company(UserMixin,db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(150))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    approval_status = db.Column(db.String(20), default='Pending')  
    is_blacklisted = db.Column(db.Boolean, default=False)

    drives = db.relationship('PlacementDrive', backref='company', lazy=True)

    def get_id(self):
        return f"Company-{self.id}"
    
class PlacementDrive(db.Model): 
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    drive_name= db.Column(db.String(150), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    application_deadline = db.Column(db.Date)
    salary = db.Column(db.String(100))
    location = db.Column(db.String(150))
    status = db.Column(db.String(20), default='Active')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='drive', lazy=True)
    
class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)

    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Applied')

    student = db.relationship('Student', backref='applications')
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),
    )

