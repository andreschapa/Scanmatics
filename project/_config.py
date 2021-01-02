import os

basedir =os.path.abspath(os.path.dirname(__file__))

DATABASE='scanmatics.db'
USERNAME='admin'
PASSWORD='admin'

CSRF_ENABLED = True
SECRET_KEY = 'myprecious'
#full path for the database
DATABASE_PATH=os.path.join(basedir, DATABASE)
SQLALCHEMY_DATABASE_URI= 'sqlite:///' + DATABASE_PATH