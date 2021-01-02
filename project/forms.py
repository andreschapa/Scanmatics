from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired

class AddCustomerForm(Form):
    customer_id=IntegerField()
    name=StringField('Customer Name', validators=[DataRequired()])