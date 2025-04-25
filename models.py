from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    current_grade = db.Column(db.String(20))
    current_rank = db.Column(db.String(20))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    national_id = db.Column(db.String(20), unique=True)
    salary = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    profile_image = db.Column(db.String(200))
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee', lazy='dynamic')
    leaves = db.relationship('Leave', backref='employee', lazy='dynamic')
    promotions = db.relationship('Promotion', backref='employee', lazy='dynamic')
    missions = db.relationship('Mission', backref='employee', lazy='dynamic')
    documents = db.relationship('Document', backref='employee', lazy='dynamic')
    
    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='present')  # present, absent, late
    
    def __repr__(self):
        return f'<Attendance {self.date} - {self.status}>'

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # vacation, sick, maternity, etc.
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    reason = db.Column(db.Text)
    document_reference = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Leave {self.leave_type} from {self.start_date} to {self.end_date}>'

class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    promotion_type = db.Column(db.String(20), nullable=False)  # 'grade' or 'rank'
    old_value = db.Column(db.String(50), nullable=False)
    new_value = db.Column(db.String(50), nullable=False)
    effective_date = db.Column(db.Date, nullable=False)
    reference_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Promotion {self.promotion_type} to {self.new_value} on {self.effective_date}>'

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='planned')  # planned, ongoing, completed
    reference_number = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Mission {self.title} from {self.start_date} to {self.end_date}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200))
    issue_date = db.Column(db.Date, default=datetime.utcnow)
    reference_number = db.Column(db.String(50), unique=True)
    generated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Document {self.document_type} - {self.reference_number}>'
