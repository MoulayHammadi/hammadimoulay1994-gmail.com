from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional, Length
from datetime import date

class DocumentForm(FlaskForm):
    # Basic document information
    document_type = SelectField('نوع المستند', validators=[DataRequired(message='يرجى اختيار نوع المستند')], choices=[
        ('work_certificate', 'شهادة عمل'),
        ('salary_statement', 'كشف راتب'),
        ('leave_permission', 'إذن إجازة'),
        ('sick_leave', 'إجازة مرضية'),
        ('maternity_leave', 'إجازة أمومة'),
        ('mission_order', 'أمر بمهمة'),
        ('grade_promotion', 'ترقية في الدرجة'),
        ('rank_promotion', 'ترقية في الرتبة'),
        ('attendance_report', 'تقرير الحضور اليومي'),
        ('employee_id_card', 'بطاقة موظف'),
        ('experience_certificate', 'شهادة خبرة مهنية'),
        ('work_start_declaration', 'تصريح بمباشرة العمل'),
        ('work_end_declaration', 'تصريح بعدم مباشرة العمل'),
        ('return_to_work', 'شهادة استئناف العمل')
    ])
    
    title = StringField('عنوان المستند', validators=[
        DataRequired(message='يرجى إدخال عنوان المستند'),
        Length(max=200, message='العنوان يجب ألا يتجاوز 200 حرف')
    ])
    
    employee_id = SelectField('الموظف', validators=[
        DataRequired(message='يرجى اختيار الموظف')
    ], coerce=int)
    
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    
    # Fields for leave permissions
    leave_type = SelectField('نوع الإجازة', validators=[Optional()], choices=[
        ('annual', 'إجازة سنوية'),
        ('sick', 'إجازة مرضية'),
        ('maternity', 'إجازة أمومة'),
        ('exceptional', 'إجازة استثنائية'),
        ('unpaid', 'إجازة بدون أجر')
    ])
    
    # Fields for date ranges (used in several document types)
    start_date = DateField('تاريخ البداية', validators=[Optional()])
    end_date = DateField('تاريخ النهاية', validators=[Optional()])
    
    # Fields for mission orders
    mission_title = StringField('عنوان المهمة', validators=[Optional()])
    mission_location = StringField('مكان المهمة', validators=[Optional()])
    
    # Fields for promotions
    old_value = StringField('القيمة القديمة', validators=[Optional()])
    new_value = StringField('القيمة الجديدة', validators=[Optional()])
    effective_date = DateField('تاريخ السريان', validators=[Optional()])
    
    # Fields for experience certificates
    years_of_service = IntegerField('سنوات الخدمة', validators=[Optional()])
    positions_held = TextAreaField('المناصب التي شغلها', validators=[Optional()])
    accomplishments = TextAreaField('الإنجازات', validators=[Optional()])
    
    # Fields for leave/work declarations
    reason = TextAreaField('السبب', validators=[Optional()])
    
    # Reference to previous leave for return to work certificates
    previous_leave_id = SelectField('الإجازة السابقة', validators=[Optional()], coerce=int)
    
    submit = SubmitField('إنشاء المستند')
    
    def validate_end_date(self, end_date):
        if end_date.data and self.start_date.data and end_date.data < self.start_date.data:
            raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')


class DocumentSearchForm(FlaskForm):
    search = StringField('بحث', validators=[Optional()])
    document_type = SelectField('نوع المستند', validators=[Optional()], choices=[
        ('', 'الكل'),
        ('work_certificate', 'شهادة عمل'),
        ('salary_statement', 'كشف راتب'),
        ('leave_permission', 'إذن إجازة'),
        ('sick_leave', 'إجازة مرضية'),
        ('maternity_leave', 'إجازة أمومة'),
        ('mission_order', 'أمر بمهمة'),
        ('grade_promotion', 'ترقية في الدرجة'),
        ('rank_promotion', 'ترقية في الرتبة'),
        ('attendance_report', 'تقرير الحضور اليومي'),
        ('employee_id_card', 'بطاقة موظف'),
        ('experience_certificate', 'شهادة خبرة مهنية'),
        ('work_start_declaration', 'تصريح بمباشرة العمل'),
        ('work_end_declaration', 'تصريح بعدم مباشرة العمل'),
        ('return_to_work', 'شهادة استئناف العمل')
    ])
    date_from = DateField('من تاريخ', validators=[Optional()])
    date_to = DateField('إلى تاريخ', validators=[Optional()])
    submit = SubmitField('بحث')
    
    def validate_date_to(self, date_to):
        if date_to.data and self.date_from.data and date_to.data < self.date_from.data:
            raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')
