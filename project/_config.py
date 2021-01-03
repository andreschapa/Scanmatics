import os

basedir =os.path.abspath(os.path.dirname(__file__))

DATABASE='scanmatics.db'

CSRF_ENABLED = True
SECRET_KEY = 'myprecious'
#full path for the database
DATABASE_PATH=os.path.join(basedir, DATABASE)
SQLALCHEMY_DATABASE_URI= 'sqlite:///' + DATABASE_PATH