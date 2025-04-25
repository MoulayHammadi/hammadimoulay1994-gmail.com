from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import arabic_reshaper
from bidi.algorithm import get_display
import io

# Register Arabic fonts
script_dir = os.path.dirname(os.path.abspath(__file__))
fonts_dir = os.path.join(script_dir, '..', 'static', 'fonts')

# Make sure the fonts directory exists
os.makedirs(fonts_dir, exist_ok=True)

# Register fonts
try:
    pdfmetrics.registerFont(TTFont('Arabic', os.path.join(fonts_dir, 'Arial.ttf')))
    pdfmetrics.registerFont(TTFont('ArabicBold', os.path.join(fonts_dir, 'Arial_Bold.ttf')))
except:
    # Fallback to DejaVuSans which has some Arabic support
    pdfmetrics.registerFont(TTFont('Arabic', os.path.join(fonts_dir, 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('ArabicBold', os.path.join(fonts_dir, 'DejaVuSans-Bold.ttf')))

# Custom styles for Arabic text
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='Arabic',
    fontName='Arabic',
    fontSize=12,
    leading=14,
    alignment=1,  # center alignment
))
styles.add(ParagraphStyle(
    name='ArabicTitle',
    fontName='ArabicBold',
    fontSize=16,
    leading=18,
    alignment=1,  # center alignment
    spaceAfter=12,
))
styles.add(ParagraphStyle(
    name='ArabicHeader',
    fontName='ArabicBold',
    fontSize=14,
    leading=16,
    alignment=1,  # center alignment
))
styles.add(ParagraphStyle(
    name='ArabicRight',
    fontName='Arabic',
    fontSize=12,
    leading=14,
    alignment=2,  # right alignment
))

def process_arabic_text(text):
    """Process Arabic text for proper display in PDF."""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def create_document_header(canvas, doc, title, reference_number, logo_path=None):
    """Create a standard header for all documents."""
    canvas.saveState()
    
    # Draw logo if available
    if logo_path and os.path.exists(logo_path):
        canvas.drawImage(logo_path, 50, 750, width=70, height=70)
    
    # Draw title
    canvas.setFont('ArabicBold', 18)
    canvas.drawCentredString(300, 800, process_arabic_text("الجمهورية الجزائرية الديمقراطية الشعبية"))
    canvas.drawCentredString(300, 780, process_arabic_text("وزارة ..."))
    canvas.drawCentredString(300, 760, process_arabic_text("مؤسسة ..."))
    
    # Draw line
    canvas.setLineWidth(1)
    canvas.line(50, 740, 550, 740)
    
    # Draw document title
    canvas.setFont('ArabicBold', 16)
    canvas.drawCentredString(300, 720, process_arabic_text(title))
    
    # Draw reference number
    canvas.setFont('Arabic', 10)
    canvas.drawRightString(550, 700, process_arabic_text(f"رقم المرجع: {reference_number}"))
    canvas.drawRightString(550, 685, process_arabic_text(f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}"))
    
    canvas.restoreState()

def create_document_footer(canvas, doc):
    """Create a standard footer for all documents."""
    canvas.saveState()
    canvas.setFont('Arabic', 10)
    canvas.drawCentredString(300, 30, process_arabic_text("هذه الوثيقة تم إنشاؤها إلكترونيًا وهي صالحة بدون توقيع"))
    canvas.drawCentredString(300, 15, process_arabic_text("© نظام إدارة الموارد البشرية"))
    canvas.restoreState()

def create_signature_section(story):
    """Add a signature section to a document."""
    story.append(Spacer(1, 20))
    
    # Create signature table
    signature_data = [
        [process_arabic_text("المدير"), "", process_arabic_text("المسؤول")],
        ["", "", ""],
        ["", "", ""],
        ["_________________", "", "_________________"]
    ]
    
    signature_table = Table(signature_data, colWidths=[150, 150, 150])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONT', (0, 0), (-1, 0), 'ArabicBold'),
        ('FONT', (0, 1), (-1, -1), 'Arabic'),
    ]))
    
    story.append(signature_table)

# Document generation functions

def generate_work_certificate(employee, output_path, reference):
    """Generate a work certificate for an employee."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Title
    title = process_arabic_text("شهادة عمل")
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Content
    content = f"""
    نشهد نحن الموقعون أدناه، أن السيد(ة) {employee.first_name} {employee.last_name}، 
    حامل(ة) رقم التعريف {employee.national_id}، يعمل لدينا كـ {employee.position} في قسم {employee.department}
    منذ {employee.hire_date.strftime('%Y-%m-%d')} وحتى تاريخه.
    
    وقد أعطيت هذه الشهادة للمعني(ة) بالأمر بناءً على طلبه(ا) للاستعمال عند الحاجة.
    """
    
    story.append(Paragraph(process_arabic_text(content), styles["ArabicRight"]))
    story.append(Spacer(1, 40))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, "شهادة عمل", reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, "شهادة عمل", reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_salary_statement(employee, output_path, reference):
    """Generate a salary statement for an employee."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Title
    title = process_arabic_text("كشف الراتب")
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Employee Information
    emp_info = f"""
    الاسم: {employee.first_name} {employee.last_name}
    رقم الموظف: {employee.employee_id}
    المنصب: {employee.position}
    القسم: {employee.department}
    الرتبة: {employee.current_rank or 'غير محدد'}
    الدرجة: {employee.current_grade or 'غير محدد'}
    """
    
    story.append(Paragraph(process_arabic_text(emp_info), styles["ArabicRight"]))
    story.append(Spacer(1, 20))
    
    # Salary details - this would normally be calculated from other tables
    # For now we'll use placeholder values
    current_month = datetime.now().strftime('%B %Y')
    
    # Sample salary components
    base_salary = employee.salary or 0
    allowances = base_salary * 0.15  # Example: 15% allowances
    deductions = base_salary * 0.08  # Example: 8% deductions for taxes, social security, etc.
    net_salary = base_salary + allowances - deductions
    
    # Create salary table
    salary_data = [
        [process_arabic_text("البند"), process_arabic_text("المبلغ (دج)")],
        [process_arabic_text("الراتب الأساسي"), f"{base_salary:,.2f}"],
        [process_arabic_text("البدلات والعلاوات"), f"{allowances:,.2f}"],
        [process_arabic_text("الخصومات"), f"{deductions:,.2f}"],
        [process_arabic_text("صافي الراتب"), f"{net_salary:,.2f}"]
    ]
    
    # Create table
    salary_table = Table(salary_data, colWidths=[300, 150])
    salary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, 0), 'ArabicBold'),
        ('FONT', (0, 1), (-1, -1), 'Arabic'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(salary_table)
    story.append(Spacer(1, 40))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, "كشف الراتب", reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, "كشف الراتب", reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_leave_permission(employee, output_path, reference, leave_data):
    """Generate a leave permission document."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Map leave types to Arabic
    leave_types = {
        'annual': 'إجازة سنوية',
        'sick': 'إجازة مرضية',
        'maternity': 'إجازة أمومة',
        'exceptional': 'إجازة استثنائية',
        'unpaid': 'إجازة بدون أجر'
    }
    
    # Title
    leave_type_ar = leave_types.get(leave_data['leave_type'], leave_data['leave_type'])
    title = process_arabic_text(f"إذن {leave_type_ar}")
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Content
    start_date = leave_data['start_date'].strftime('%Y-%m-%d')
    end_date = leave_data['end_date'].strftime('%Y-%m-%d')
    
    content = f"""
    بناءً على الطلب المقدم من طرف السيد(ة) {employee.first_name} {employee.last_name}، 
    حامل(ة) رقم التعريف {employee.national_id}، 
    الذي يشغل منصب {employee.position} في قسم {employee.department}،
    
    نمنح للمعني(ة) بالأمر {leave_type_ar} لمدة {(leave_data['end_date'] - leave_data['start_date']).days + 1} يوم(أيام)،
    ابتداءً من تاريخ {start_date} إلى غاية {end_date}.
    """
    
    if leave_data.get('reason'):
        content += f"\nوذلك للسبب التالي: {leave_data['reason']}"
    
    story.append(Paragraph(process_arabic_text(content), styles["ArabicRight"]))
    story.append(Spacer(1, 40))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, f"إذن {leave_type_ar}", reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, f"إذن {leave_type_ar}", reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_mission_order(employee, output_path, reference, mission_data):
    """Generate a mission order document."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Title
    title = process_arabic_text("أمر بمهمة")
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Content
    start_date = mission_data['start_date'].strftime('%Y-%m-%d')
    end_date = mission_data['end_date'].strftime('%Y-%m-%d')
    
    content = f"""
    بناءً على احتياجات المصلحة، نأمر السيد(ة) {employee.first_name} {employee.last_name}، 
    حامل(ة) رقم التعريف {employee.national_id}، الذي يشغل منصب {employee.position} في قسم {employee.department}،
    
    بالقيام بمهمة بعنوان "{mission_data['title']}" في {mission_data['location']}،
    وذلك لمدة {(mission_data['end_date'] - mission_data['start_date']).days + 1} يوم(أيام)،
    ابتداءً من تاريخ {start_date} إلى غاية {end_date}.
    """
    
    if mission_data.get('description'):
        content += f"\nوصف المهمة: {mission_data['description']}"
    
    story.append(Paragraph(process_arabic_text(content), styles["ArabicRight"]))
    story.append(Spacer(1, 40))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, "أمر بمهمة", reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, "أمر بمهمة", reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_promotion_document(employee, output_path, reference, promotion_data):
    """Generate a promotion document."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Map promotion types to Arabic
    promotion_types = {
        'grade': 'الترقية في الدرجة',
        'rank': 'الترقية في الرتبة'
    }
    
    promotion_type_ar = promotion_types.get(promotion_data['promotion_type'], promotion_data['promotion_type'])
    
    # Title
    title = process_arabic_text(promotion_type_ar)
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Content
    effective_date = promotion_data['effective_date'].strftime('%Y-%m-%d')
    
    content = f"""
    بناءً على القوانين واللوائح المنظمة للترقيات في المؤسسة، 
    وبعد النظر في ملف السيد(ة) {employee.first_name} {employee.last_name}، 
    حامل(ة) رقم التعريف {employee.national_id}، الذي يشغل منصب {employee.position} في قسم {employee.department}،
    
    نقرر منح المعني(ة) بالأمر {promotion_type_ar} من {promotion_data['old_value']} إلى {promotion_data['new_value']}،
    وذلك ابتداءً من تاريخ {effective_date}.
    """
    
    if promotion_data.get('notes'):
        content += f"\nملاحظات: {promotion_data['notes']}"
    
    story.append(Paragraph(process_arabic_text(content), styles["ArabicRight"]))
    story.append(Spacer(1, 40))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, promotion_type_ar, reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, promotion_type_ar, reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_attendance_report(employee, output_path, reference, attendance_records, date_from, date_to):
    """Generate an attendance report for an employee."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Title
    title = process_arabic_text("تقرير الحضور")
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 10))
    
    # Period subtitle
    period = f"للفترة من {date_from.strftime('%Y-%m-%d')} إلى {date_to.strftime('%Y-%m-%d')}"
    story.append(Paragraph(process_arabic_text(period), styles["ArabicHeader"]))
    story.append(Spacer(1, 20))
    
    # Employee information
    emp_info = f"""
    الاسم: {employee.first_name} {employee.last_name}
    رقم الموظف: {employee.employee_id}
    المنصب: {employee.position}
    القسم: {employee.department}
    """
    
    story.append(Paragraph(process_arabic_text(emp_info), styles["ArabicRight"]))
    story.append(Spacer(1, 20))
    
    # Status mapping
    status_map = {
        'present': 'حاضر',
        'absent': 'غائب',
        'late': 'متأخر'
    }
    
    # Create attendance table
    attendance_data = [
        [process_arabic_text("التاريخ"), process_arabic_text("وقت الحضور"), 
         process_arabic_text("وقت الانصراف"), process_arabic_text("الحالة")]
    ]
    
    for record in attendance_records:
        check_in_time = record.check_in.strftime('%H:%M') if record.check_in else '-'
        check_out_time = record.check_out.strftime('%H:%M') if record.check_out else '-'
        status_ar = status_map.get(record.status, record.status)
        
        attendance_data.append([
            record.date.strftime('%Y-%m-%d'),
            check_in_time,
            check_out_time,
            process_arabic_text(status_ar)
        ])
    
    # If no records, add a message
    if not attendance_records:
        attendance_data.append([process_arabic_text("لا توجد سجلات حضور للفترة المحددة"), "", "", ""])
    
    # Create table
    attendance_table = Table(attendance_data, colWidths=[100, 100, 100, 150])
    attendance_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, 0), 'ArabicBold'),
        ('FONT', (0, 1), (-1, -1), 'Arabic'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(attendance_table)
    story.append(Spacer(1, 40))
    
    # Summary
    present_count = sum(1 for record in attendance_records if record.status == 'present')
    absent_count = sum(1 for record in attendance_records if record.status == 'absent')
    late_count = sum(1 for record in attendance_records if record.status == 'late')
    total_days = len(attendance_records)
    
    summary = f"""
    ملخص الحضور:
    عدد أيام الحضور: {present_count} ({present_count/total_days*100:.1f}% من الإجمالي)
    عدد أيام الغياب: {absent_count} ({absent_count/total_days*100:.1f}% من الإجمالي)
    عدد أيام التأخير: {late_count} ({late_count/total_days*100:.1f}% من الإجمالي)
    """
    
    if total_days > 0:
        story.append(Paragraph(process_arabic_text(summary), styles["ArabicRight"]))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, "تقرير الحضور", reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, "تقرير الحضور", reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_employee_id_card(employee, output_path, reference):
    """Generate an employee ID card."""
    # ID cards should be credit card sized but we'll use a scaled version on A4 for now
    # In a real app, you might use a card printer or special templates
    
    buffer = io.BytesIO()
    width, height = 350, 220  # ID card dimensions (scaled)
    
    # Create card canvas
    c = canvas.Canvas(buffer, pagesize=(width, height))
    c.setTitle(f"Employee ID Card - {employee.first_name} {employee.last_name}")
    
    # Set background color
    c.setFillColor(colors.lightblue)
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Draw header
    c.setFillColor(colors.white)
    c.rect(0, height-40, width, 40, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('ArabicBold', 12)
    c.drawCentredString(width/2, height-20, process_arabic_text("بطاقة هوية موظف"))
    c.drawCentredString(width/2, height-35, process_arabic_text("مؤسسة ..."))
    
    # Draw employee image placeholder
    if employee.profile_image and os.path.exists(employee.profile_image):
        c.drawImage(employee.profile_image, 20, height-120, width=80, height=70)
    else:
        c.setFillColor(colors.white)
        c.rect(20, height-120, 80, 70, fill=True, stroke=True)
        c.setFillColor(colors.black)
        c.setFont('Arabic', 8)
        c.drawCentredString(60, height-90, "صورة")
    
    # Draw employee information
    c.setFont('Arabic', 10)
    c.drawRightString(340, height-60, process_arabic_text(f"الاسم: {employee.first_name} {employee.last_name}"))
    c.drawRightString(340, height-80, process_arabic_text(f"رقم الموظف: {employee.employee_id}"))
    c.drawRightString(340, height-100, process_arabic_text(f"المنصب: {employee.position}"))
    c.drawRightString(340, height-120, process_arabic_text(f"القسم: {employee.department}"))
    
    # Draw footer
    c.setFillColor(colors.white)
    c.rect(0, 0, width, 30, fill=True, stroke=False)
    
    c.setFillColor(colors.black)
    c.setFont('Arabic', 8)
    c.drawCentredString(width/2, 15, process_arabic_text(f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}"))
    c.drawCentredString(width/2, 5, process_arabic_text("هذه البطاقة ملك للمؤسسة ويجب إعادتها عند انتهاء العمل"))
    
    # Save card
    c.showPage()
    c.save()
    
    # Now place the card on an A4 page as a PDF to print
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Title
    title = process_arabic_text("بطاقة هوية موظف")
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Instructions
    instructions = """
    فيما يلي بطاقة هوية الموظف. 
    يرجى طباعة هذه الصفحة، وقص البطاقة على طول الخطوط المتقطعة، ثم تغليفها.
    """
    story.append(Paragraph(process_arabic_text(instructions), styles["ArabicRight"]))
    story.append(Spacer(1, 20))
    
    # Add ID card image
    buffer.seek(0)
    img = Image(buffer, width=350, height=220)
    img.hAlign = 'CENTER'
    story.append(img)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, "بطاقة هوية موظف", reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, "بطاقة هوية موظف", reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_experience_certificate(employee, output_path, reference, experience_data):
    """Generate an experience certificate for an employee."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Title
    title = process_arabic_text("شهادة خبرة مهنية")
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Content
    years_of_service = experience_data.get('years_of_service', 
                                         (datetime.now().date() - employee.hire_date).days // 365)
    
    content = f"""
    نشهد نحن الموقعون أدناه، أن السيد(ة) {employee.first_name} {employee.last_name}، 
    حامل(ة) رقم التعريف {employee.national_id}، قد عمل لدينا لمدة {years_of_service} سنة/سنوات
    منذ {employee.hire_date.strftime('%Y-%m-%d')} وحتى تاريخه.
    
    خلال فترة عمله(ها)، شغل(ت) المناصب التالية:
    """
    
    story.append(Paragraph(process_arabic_text(content), styles["ArabicRight"]))
    story.append(Spacer(1, 10))
    
    # Positions held
    if experience_data.get('positions'):
        positions = experience_data['positions'].split('\n')
        for position in positions:
            story.append(Paragraph(process_arabic_text(f"• {position.strip()}"), styles["ArabicRight"]))
    else:
        story.append(Paragraph(process_arabic_text(f"• {employee.position} في {employee.department}"), styles["ArabicRight"]))
    
    story.append(Spacer(1, 10))
    
    # Accomplishments if available
    if experience_data.get('accomplishments'):
        accomplishments_text = f"""
        وقد تميز(ت) المعني(ة) بالأمر بالإنجازات التالية:
        """
        story.append(Paragraph(process_arabic_text(accomplishments_text), styles["ArabicRight"]))
        story.append(Spacer(1, 10))
        
        accomplishments = experience_data['accomplishments'].split('\n')
        for accomplishment in accomplishments:
            story.append(Paragraph(process_arabic_text(f"• {accomplishment.strip()}"), styles["ArabicRight"]))
        
        story.append(Spacer(1, 10))
    
    # Closing
    closing = """
    وقد أعطيت هذه الشهادة للمعني(ة) بالأمر بناءً على طلبه(ا) للاستعمال عند الحاجة.
    """
    story.append(Paragraph(process_arabic_text(closing), styles["ArabicRight"]))
    story.append(Spacer(1, 40))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, "شهادة خبرة مهنية", reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, "شهادة خبرة مهنية", reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_work_declaration(employee, output_path, reference, declaration_data):
    """Generate a work start/end declaration."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Determine title based on declaration type
    if declaration_data['declaration_type'] == 'start':
        title_ar = "تصريح بمباشرة العمل"
    else:
        title_ar = "تصريح بعدم مباشرة العمل"
    
    # Title
    title = process_arabic_text(title_ar)
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Content
    effective_date = declaration_data['effective_date'].strftime('%Y-%m-%d')
    
    if declaration_data['declaration_type'] == 'start':
        content = f"""
        أنا الموقع أدناه، أصرح بأن السيد(ة) {employee.first_name} {employee.last_name}، 
        حامل(ة) رقم التعريف {employee.national_id}، قد باشر(ت) عمله(ها) كـ {employee.position} في قسم {employee.department}
        اعتباراً من تاريخ {effective_date}.
        """
    else:
        content = f"""
        أنا الموقع أدناه، أصرح بأن السيد(ة) {employee.first_name} {employee.last_name}، 
        حامل(ة) رقم التعريف {employee.national_id}، قد توقف(ت) عن مباشرة عمله(ها) كـ {employee.position} في قسم {employee.department}
        اعتباراً من تاريخ {effective_date}.
        """
    
    if declaration_data.get('reason'):
        content += f"\nوذلك للسبب التالي: {declaration_data['reason']}"
    
    story.append(Paragraph(process_arabic_text(content), styles["ArabicRight"]))
    story.append(Spacer(1, 40))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, title_ar, reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, title_ar, reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

def generate_return_certificate(employee, output_path, reference, return_data):
    """Generate a return to work certificate."""
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    story = []
    
    # Title
    title = process_arabic_text("شهادة استئناف العمل")
    story.append(Paragraph(title, styles["ArabicTitle"]))
    story.append(Spacer(1, 20))
    
    # Content
    return_date = return_data['return_date'].strftime('%Y-%m-%d')
    
    content = f"""
    أنا الموقع أدناه، أشهد بأن السيد(ة) {employee.first_name} {employee.last_name}، 
    حامل(ة) رقم التعريف {employee.national_id}، قد استأنف(ت) عمله(ها) كـ {employee.position} في قسم {employee.department}
    اعتباراً من تاريخ {return_date}.
    """
    
    # If there's a previous leave, add details
    if return_data.get('previous_leave'):
        leave = return_data['previous_leave']
        leave_start = leave.start_date.strftime('%Y-%m-%d')
        leave_end = leave.end_date.strftime('%Y-%m-%d')
        
        leave_types = {
            'annual': 'إجازة سنوية',
            'sick': 'إجازة مرضية',
            'maternity': 'إجازة أمومة',
            'exceptional': 'إجازة استثنائية',
            'unpaid': 'إجازة بدون أجر'
        }
        
        leave_type_ar = leave_types.get(leave.leave_type, leave.leave_type)
        
        content += f"""
        وذلك بعد انتهاء {leave_type_ar} التي استفاد(ت) منها 
        للفترة من {leave_start} إلى {leave_end}.
        """
    
    if return_data.get('notes'):
        content += f"\nملاحظات: {return_data['notes']}"
    
    story.append(Paragraph(process_arabic_text(content), styles["ArabicRight"]))
    story.append(Spacer(1, 40))
    
    # Add signature section
    create_signature_section(story)
    
    # Build document with custom header and footer
    doc.build(story, onFirstPage=lambda canvas, doc: create_document_header(canvas, doc, "شهادة استئناف العمل", reference),
              onLaterPages=lambda canvas, doc: create_document_header(canvas, doc, "شهادة استئناف العمل", reference),
              canvasmaker=NumberedCanvas)
    
    return output_path

# Helper class for page numbers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page numbers to each page and save"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setFont("Arabic", 9)
            self.drawRightString(550, 30, process_arabic_text(f"صفحة {self._pageNumber} من {num_pages}"))
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
