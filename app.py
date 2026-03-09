from flask import Flask
from flask_login import LoginManager    
from models import db, Admin, Student, Company,PlacementDrive, Application
from werkzeug.security import generate_password_hash
from auth import auth_bp
from admin import admin_bp
from company import company_bp
from student import student_bp

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placement_portal.db'   
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='placement-portal-secret-key'

db.init_app(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(company_bp)
app.register_blueprint(student_bp)
@login_manager.user_loader
def load_user(user_id):
    role, user_id = user_id.split("-")
    user_id = int(user_id)

    if role == "Admin":
        return db.session.get(Admin, user_id)
    elif role == "Student":
        return db.session.get(Student, user_id)
    elif role == "Company":
        return db.session.get(Company, user_id)

    return None

def create_admin():
    admin = Admin.query.filter_by(username='admin').first()

    if not admin:
        new_admin = Admin(
            username='admin',
            password=generate_password_hash('admin123')
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Default admin created")
    else:
        print("ℹ️ Admin already exists")

with app.app_context():
    db.create_all()
    create_admin()




if __name__ == '__main__':
    app.run(debug=True, port=5001)
