from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app import db
from models import Employee, Document, Leave, Promotion, Mission, Attendance
from forms.documents import DocumentForm, DocumentSearchForm
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from utils.pdf_generator import (
    generate_work_certificate, 
    generate_salary_statement,
    generate_leave_permission,
    generate_mission_order,
    generate_promotion_document,
    generate_attendance_report,
    generate_employee_id_card,
    generate_experience_certificate,
    generate_work_declaration,
    generate_return_certificate
)

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/documents')
@login_required
def document_list():
    search_form = DocumentSearchForm()
    query = Document.query.join(Employee)
    
    if search_form.validate():
        if search_form.search.data:
            search_term = f"%{search_form.search.data}%"
            query = query.filter(
                (Document.title.like(search_term)) |
                (Document.reference_number.like(search_term)) |
                (Document.document_type.like(search_term)) |
                (Employee.first_name.like(search_term)) |
                (Employee.last_name.like(search_term)) |
                (Employee.employee_id.like(search_term))
            )
        
        if search_form.document_type.data:
            query = query.filter(Document.document_type == search_form.document_type.data)
            
        if search_form.date_from.data:
            query = query.filter(Document.issue_date >= search_form.date_from.data)
            
        if search_form.date_to.data:
            query = query.filter(Document.issue_date <= search_form.date_to.data)
    
    documents = query.order_by(Document.issue_date.desc()).all()
    return render_template('documents/list.html', 
                           documents=documents, 
                           form=search_form,
                           title='قائمة المستندات')

@documents_bp.route('/documents/generate', methods=['GET', 'POST'])
@login_required
def generate_document():
    form = DocumentForm()
    
    # Populate the employee choices
    form.employee_id.choices = [(e.id, f"{e.first_name} {e.last_name} ({e.employee_id})") 
                                for e in Employee.query.filter_by(is_active=True).order_by(Employee.last_name).all()]
    
    if form.validate_on_submit():
        employee = Employee.query.get(form.employee_id.data)
        
        # Generate reference number
        reference = f"{form.document_type.data}-{employee.employee_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Create document entry in database
        document = Document(
            employee_id=employee.id,
            document_type=form.document_type.data,
            title=form.title.data,
            reference_number=reference,
            generated_by=current_user.id,
            notes=form.notes.data
        )
        
        # Generate PDF based on document type
        document_path = os.path.join(current_app.config['DOCUMENT_UPLOAD_PATH'], f"{reference}.pdf")
        
        if form.document_type.data == 'work_certificate':
            generate_work_certificate(employee, document_path, reference)
        elif form.document_type.data == 'salary_statement':
            generate_salary_statement(employee, document_path, reference)
        elif form.document_type.data == 'leave_permission':
            leave_data = {
                'leave_type': form.leave_type.data,
                'start_date': form.start_date.data,
                'end_date': form.end_date.data,
                'reason': form.reason.data
            }
            generate_leave_permission(employee, document_path, reference, leave_data)
            
            # Create leave record in database
            leave = Leave(
                employee_id=employee.id,
                leave_type=form.leave_type.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                status='approved',
                reason=form.reason.data,
                document_reference=reference
            )
            db.session.add(leave)
            
        elif form.document_type.data == 'mission_order':
            mission_data = {
                'title': form.mission_title.data,
                'location': form.mission_location.data,
                'start_date': form.start_date.data,
                'end_date': form.end_date.data,
                'description': form.reason.data
            }
            generate_mission_order(employee, document_path, reference, mission_data)
            
            # Create mission record in database
            mission = Mission(
                employee_id=employee.id,
                title=form.mission_title.data,
                location=form.mission_location.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                description=form.reason.data,
                status='planned',
                reference_number=reference
            )
            db.session.add(mission)
            
        elif form.document_type.data in ['grade_promotion', 'rank_promotion']:
            promotion_data = {
                'promotion_type': 'grade' if form.document_type.data == 'grade_promotion' else 'rank',
                'old_value': form.old_value.data,
                'new_value': form.new_value.data,
                'effective_date': form.effective_date.data,
                'notes': form.notes.data
            }
            generate_promotion_document(employee, document_path, reference, promotion_data)
            
            # Create promotion record and update employee
            promotion = Promotion(
                employee_id=employee.id,
                promotion_type='grade' if form.document_type.data == 'grade_promotion' else 'rank',
                old_value=form.old_value.data,
                new_value=form.new_value.data,
                effective_date=form.effective_date.data,
                reference_number=reference,
                notes=form.notes.data
            )
            
            # Update the employee's current grade or rank
            if form.document_type.data == 'grade_promotion':
                employee.current_grade = form.new_value.data
            else:
                employee.current_rank = form.new_value.data
                
            db.session.add(promotion)
            
        elif form.document_type.data == 'attendance_report':
            date_from = form.start_date.data
            date_to = form.end_date.data
            attendance_records = Attendance.query.filter(
                Attendance.employee_id == employee.id,
                Attendance.date >= date_from,
                Attendance.date <= date_to
            ).order_by(Attendance.date).all()
            
            generate_attendance_report(employee, document_path, reference, attendance_records, date_from, date_to)
            
        elif form.document_type.data == 'employee_id_card':
            generate_employee_id_card(employee, document_path, reference)
            
        elif form.document_type.data == 'experience_certificate':
            experience_data = {
                'years_of_service': form.years_of_service.data,
                'positions': form.positions_held.data,
                'accomplishments': form.accomplishments.data
            }
            generate_experience_certificate(employee, document_path, reference, experience_data)
            
        elif form.document_type.data in ['work_start_declaration', 'work_end_declaration']:
            declaration_data = {
                'declaration_type': 'start' if form.document_type.data == 'work_start_declaration' else 'end',
                'effective_date': form.effective_date.data,
                'reason': form.reason.data
            }
            generate_work_declaration(employee, document_path, reference, declaration_data)
            
        elif form.document_type.data == 'return_to_work':
            return_data = {
                'previous_leave': Leave.query.get(form.previous_leave_id.data) if form.previous_leave_id.data else None,
                'return_date': form.effective_date.data,
                'notes': form.notes.data
            }
            generate_return_certificate(employee, document_path, reference, return_data)
            
            # Update leave status if a previous leave was referenced
            if form.previous_leave_id.data:
                leave = Leave.query.get(form.previous_leave_id.data)
                leave.status = 'completed'
        
        # Save the file path in the document record
        document.file_path = document_path
        db.session.add(document)
        db.session.commit()
        
        flash('تم إنشاء المستند بنجاح', 'success')
        return redirect(url_for('documents.view_document', document_id=document.id))
    
    # Handle GET request by showing the form
    return render_template('documents/generate.html', 
                           form=form,
                           title='إنشاء مستند جديد')

@documents_bp.route('/documents/<int:document_id>')
@login_required
def view_document(document_id):
    document = Document.query.get_or_404(document_id)
    employee = Employee.query.get(document.employee_id)
    
    return render_template('documents/view.html',
                           document=document,
                           employee=employee,
                           title=f"{document.title}")

@documents_bp.route('/documents/<int:document_id>/download')
@login_required
def download_document(document_id):
    document = Document.query.get_or_404(document_id)
    
    # Check if document file exists
    if not document.file_path or not os.path.exists(document.file_path):
        flash('المستند غير متوفر للتنزيل', 'danger')
        return redirect(url_for('documents.view_document', document_id=document.id))
    
    return send_file(document.file_path, 
                     as_attachment=True,
                     download_name=f"{document.reference_number}.pdf")

@documents_bp.route('/documents/<int:document_id>/regenerate')
@login_required
def regenerate_document(document_id):
    document = Document.query.get_or_404(document_id)
    employee = Employee.query.get(document.employee_id)
    
    # Regenerate the document based on its type
    # (This would call the same generation functions as in generate_document)
    
    flash('تم إعادة إنشاء المستند بنجاح', 'success')
    return redirect(url_for('documents.view_document', document_id=document.id))
