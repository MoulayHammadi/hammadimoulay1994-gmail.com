from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Employee, Attendance, Leave, Promotion, Mission
from forms.employee import EmployeeForm, EmployeeSearchForm
from datetime import datetime

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/dashboard')
@login_required
def dashboard():
    # Get counts for dashboard widgets
    total_employees = Employee.query.filter_by(is_active=True).count()
    employees_on_leave = Leave.query.filter_by(status='approved').filter(
        Leave.start_date <= datetime.utcnow().date(),
        Leave.end_date >= datetime.utcnow().date()
    ).count()
    recent_documents = db.session.query(Employee).join(
        Employee.documents).order_by('document.issue_date').limit(5).all()
    
    # Get recent attendance data
    today = datetime.utcnow().date()
    today_attendance = Attendance.query.filter_by(date=today).all()
    
    return render_template('employees/dashboard.html', 
                           title='لوحة التحكم',
                           total_employees=total_employees,
                           employees_on_leave=employees_on_leave,
                           recent_documents=recent_documents,
                           today_attendance=today_attendance)

@employees_bp.route('/employees')
@login_required
def employee_list():
    search_form = EmployeeSearchForm()
    query = Employee.query
    
    if search_form.validate():
        if search_form.search.data:
            search_term = f"%{search_form.search.data}%"
            query = query.filter(
                (Employee.first_name.like(search_term)) |
                (Employee.last_name.like(search_term)) |
                (Employee.employee_id.like(search_term)) |
                (Employee.position.like(search_term)) |
                (Employee.department.like(search_term))
            )
    
    employees = query.order_by(Employee.last_name).all()
    return render_template('employees/list.html', 
                           employees=employees, 
                           form=search_form,
                           title='قائمة الموظفين')

@employees_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        # Create a new employee from form data
        employee = Employee(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            employee_id=form.employee_id.data,
            birth_date=form.birth_date.data,
            hire_date=form.hire_date.data,
            position=form.position.data,
            department=form.department.data,
            current_grade=form.current_grade.data,
            current_rank=form.current_rank.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            national_id=form.national_id.data,
            salary=form.salary.data,
            is_active=True
        )
        
        # Handle profile image upload if provided
        if form.profile_image.data:
            filename = secure_filename(f"{employee.employee_id}_{int(datetime.utcnow().timestamp())}.jpg")
            form.profile_image.data.save(os.path.join('static/uploads/profile_images', filename))
            employee.profile_image = filename
        
        db.session.add(employee)
        db.session.commit()
        
        flash('تمت إضافة الموظف بنجاح', 'success')
        return redirect(url_for('employees.employee_detail', employee_id=employee.id))
    
    return render_template('employees/add_edit.html', 
                           form=form, 
                           title='إضافة موظف جديد',
                           is_add=True)

@employees_bp.route('/employees/<int:employee_id>')
@login_required
def employee_detail(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Get related data for this employee
    attendance_records = employee.attendance_records.order_by(Attendance.date.desc()).limit(10).all()
    leaves = employee.leaves.order_by(Leave.start_date.desc()).limit(5).all()
    promotions = employee.promotions.order_by(Promotion.effective_date.desc()).limit(5).all()
    missions = employee.missions.order_by(Mission.start_date.desc()).limit(5).all()
    documents = employee.documents.order_by('document.issue_date').limit(10).all()
    
    return render_template('employees/detail.html', 
                           employee=employee,
                           attendance_records=attendance_records,
                           leaves=leaves,
                           promotions=promotions,
                           missions=missions,
                           documents=documents,
                           title=f"الملف الشخصي - {employee.first_name} {employee.last_name}")

@employees_bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm(obj=employee)
    
    if form.validate_on_submit():
        # Update employee from form data
        form.populate_obj(employee)
        
        # Handle profile image upload if provided
        if form.profile_image.data:
            filename = secure_filename(f"{employee.employee_id}_{int(datetime.utcnow().timestamp())}.jpg")
            form.profile_image.data.save(os.path.join('static/uploads/profile_images', filename))
            employee.profile_image = filename
        
        db.session.commit()
        flash('تم تحديث بيانات الموظف بنجاح', 'success')
        return redirect(url_for('employees.employee_detail', employee_id=employee.id))
    
    return render_template('employees/add_edit.html', 
                           form=form, 
                           employee=employee,
                           title='تعديل بيانات الموظف',
                           is_add=False)

@employees_bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    # Instead of deleting, mark as inactive
    employee.is_active = False
    db.session.commit()
    
    flash('تم حذف الموظف بنجاح', 'success')
    return redirect(url_for('employees.employee_list'))

@employees_bp.route('/employees/<int:employee_id>/activate', methods=['POST'])
@login_required
def activate_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    
    employee.is_active = True
    db.session.commit()
    
    flash('تم تفعيل حساب الموظف بنجاح', 'success')
    return redirect(url_for('employees.employee_detail', employee_id=employee.id))
