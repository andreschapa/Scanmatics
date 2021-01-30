#project/__init__.py

import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt




app = Flask(__name__)
app.config.from_pyfile('_config.py')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from project.main.views import main_blueprint
app.register_blueprint(main_blueprint)

from itsdangerous import URLSafeTimedSerializer


