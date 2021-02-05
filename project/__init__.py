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
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": 'main@scanmatics.com',
    "MAIL_PASSWORD": 'viegvulcogqqnzrh'
}

app.config.update(mail_settings)
mail = Mail(app)

if __name__ == '__main__':
    with app.app_context():
        msg = Message(subject="Hello",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=["andres.chapa@iidm.com"], # replace with your email for testing
                      body="This is a test email I sent with Gmail and Python!")
        mail.send(msg)


