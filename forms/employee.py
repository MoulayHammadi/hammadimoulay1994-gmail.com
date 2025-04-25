from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, BooleanField, SelectField, DateField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError
from datetime import date

class EmployeeForm(FlaskForm):
    # Personal Information
    first_name = StringField('الاسم الأول', validators=[
        DataRequired(message='يرجى إدخال الاسم الأول')
    ])
    last_name = StringField('اللقب', validators=[
        DataRequired(message='يرجى إدخال اللقب')
    ])
    employee_id = StringField('رقم الموظف', validators=[
        DataRequired(message='يرجى إدخال رقم الموظف'),
        Length(min=4, max=20, message='رقم الموظف يجب أن يكون بين 4 و 20 حرفًا')
    ])
    national_id = StringField('رقم الهوية الوطنية', validators=[
        DataRequired(message='يرجى إدخال رقم الهوية الوطنية')
    ])
    birth_date = DateField('تاريخ الميلاد', validators=[
        DataRequired(message='يرجى إدخال تاريخ الميلاد')
    ])
    
    # Employment Information
    hire_date = DateField('تاريخ التوظيف', validators=[
        DataRequired(message='يرجى إدخال تاريخ التوظيف')
    ])
    position = StringField('المنصب', validators=[
        DataRequired(message='يرجى إدخال المنصب')
    ])
    department = StringField('القسم', validators=[
        DataRequired(message='يرجى إدخال القسم')
    ])
    current_grade = StringField('الدرجة الحالية', validators=[Optional()])
    current_rank = StringField('الرتبة الحالية', validators=[Optional()])
    salary = FloatField('الراتب', validators=[Optional()])
    
    # Contact Information
    address = TextAreaField('العنوان', validators=[Optional()])
    phone = StringField('رقم الهاتف', validators=[Optional()])
    email = StringField('البريد الإلكتروني', validators=[
        Optional(), 
        Email(message='يرجى إدخال بريد إلكتروني صالح')
    ])
    
    # Profile Image
    profile_image = FileField('صورة الملف الشخصي', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], message='الصور المسموح بها: jpg, png, jpeg')
    ])
    
    submit = SubmitField('حفظ')
    
    def validate_birth_date(self, birth_date):
        if birth_date.data >= date.today():
            raise ValidationError('تاريخ الميلاد يجب أن يكون في الماضي')
            
    def validate_hire_date(self, hire_date):
        if hire_date.data > date.today():
            raise ValidationError('تاريخ التوظيف لا يمكن أن يكون في المستقبل')
            
        if self.birth_date.data and hire_date.data <= self.birth_date.data:
            raise ValidationError('تاريخ التوظيف يجب أن يكون بعد تاريخ الميلاد')


class EmployeeSearchForm(FlaskForm):
    search = StringField('بحث', validators=[Optional()])
    department = SelectField('القسم', validators=[Optional()], choices=[])
    position = SelectField('المنصب', validators=[Optional()], choices=[])
    status = SelectField('الحالة', validators=[Optional()], choices=[
        ('', 'الكل'),
        ('active', 'نشط'),
        ('inactive', 'غير نشط')
    ])
    submit = SubmitField('بحث')
    
    def __init__(self, *args, **kwargs):
        super(EmployeeSearchForm, self).__init__(*args, **kwargs)
        # The department and position choices will be populated dynamically 
        # when the form is instantiated in the route handler
