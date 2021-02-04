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

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT']= 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME']='main@scanmatics.com'
app.config['MAIL_PASSWORD']='Scanmatics2020!'

mail = Mail(app)


