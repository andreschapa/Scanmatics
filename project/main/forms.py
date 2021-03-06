from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email
import datetime

class RegisterQRForm(Form):

    panel_id=IntegerField('Panel ID', validators=[DataRequired()])
    end_user=StringField('End User', validators=[DataRequired()])
    panel_name=StringField('Panel Name', validators=[DataRequired()])



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
        validators=[DataRequired(), Email(), Length(min=6, max=40)]
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
   

class AddProjectForm(Form):
    project_id=IntegerField()
    name=StringField('Project Name', validators=[DataRequired()])

class AddPanelForm(Form):
    panel_id=IntegerField()
    name=StringField('Panel Name', validators=[DataRequired()])

class RequestResetForm(Form):
    email= StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(min=6, max=40)])
    submit=SubmitField('Request Password Reset')

class ResetPasswordForm(Form):
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=40)])
    confirm= PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit=SubmitField('Reset Password')
    

class SendEmailLink(Form):
    email= StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(min=6, max=40)])

class AddMaintenanceLog(Form):
    MaintenanceLog_id = IntegerField()
    MaintenanceLog_panel_id= IntegerField()
    maintenance_issue = StringField('Maintenance Issue', validators=[DataRequired()])
    posted_date= DateField(
        'Posted Date ',
        validators=[DataRequired()], format='%m/%d/%Y'
    )
    priority = SelectField(
        'Priority',
        validators=[DataRequired()],
        choices=[
            ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
            ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')
        ]
    )
    status = IntegerField('Status')
    action_taken= StringField('Action Taken') # might have to get rid of validators since this can be nullable



