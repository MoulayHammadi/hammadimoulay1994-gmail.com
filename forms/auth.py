from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(message='يرجى إدخال اسم المستخدم')])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message='يرجى إدخال كلمة المرور')])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='يرجى إدخال اسم المستخدم'),
        Length(min=4, max=25, message='اسم المستخدم يجب أن يكون بين 4 و 25 حرفًا')
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='يرجى إدخال البريد الإلكتروني'),
        Email(message='يرجى إدخال بريد إلكتروني صالح')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='يرجى إدخال كلمة المرور'),
        Length(min=8, message='كلمة المرور يجب أن تكون 8 أحرف على الأقل')
    ])
    password2 = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='يرجى تأكيد كلمة المرور'),
        EqualTo('password', message='كلمتا المرور غير متطابقتين')
    ])
    submit = SubmitField('تسجيل')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('يرجى استخدام اسم مستخدم مختلف، هذا الاسم مستخدم بالفعل')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('يرجى استخدام بريد إلكتروني مختلف، هذا البريد مستخدم بالفعل')
