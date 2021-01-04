from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

class AddCustomerForm(Form):
    customer_id=IntegerField()
    name=StringField('Customer Name', validators=[DataRequired()])

class RegisterForm(Form):
    name= StringField(
        'Username',
        validators=[DataRequired(), Length(min=6, max=30)]
    )
    email= StringField(
        'Email',
        validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=40)])
    confirm= PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    company = StringField(
        'Company',
        validators=[DataRequired(), Length(min=3, max=40)])
    

class LoginForm(Form):
    name=StringField(
        'Username',
        validators=[DataRequired()]
    )
    password=PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    company=StringField(
        'Company',
        validators=[DataRequired()]
    )

class AddProjectForm(Form):
    project_id=IntegerField()
    name=StringField('Project Name', validators=[DataRequired()])
