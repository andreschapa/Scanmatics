#project/__init__.py

import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
 
import os


app = Flask(__name__)
app.config.from_pyfile('_config.py')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
mail = Mail(app)

from project.main.views import main_blueprint, send_reset_email
app.register_blueprint(main_blueprint)

#app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
#app.config['MAIL_PORT']= 587
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = False
#app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
#app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'main@scanmatics.com',
    "MAIL_PASSWORD": 'xuchmgcsaejdhxuq'
}

app.config.update(mail_settings)
mail = Mail(app)

mail = Mail(app)


