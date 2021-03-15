#project/__init__.py

import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_login import LoginManager ##
from flask_jwt_extended import JWTManager ##
import os


app = Flask(__name__)
app.config.from_pyfile('_config.py')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)##
jwt = JWTManager(app) ###

from project.main.views import main_blueprint, send_reset_email
app.register_blueprint(main_blueprint)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": 'main@scanmatics.com',
    "MAIL_PASSWORD": 'viegvulcogqqnzrh',

}

app.config.update(mail_settings)
mail = Mail(app)

