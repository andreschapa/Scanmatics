import os

basedir =os.path.abspath(os.path.dirname(__file__))

DATABASE='scanmatics.db'
DEBUG = True 
CSRF_ENABLED = True
SECRET_KEY = 'myprecious'
#full path for the database
DATABASE_PATH=os.path.join(basedir, DATABASE)
#SQLALCHEMY_DATABASE_URI= 'sqlite:///' + DATABASE_PATH



###changing a few things to create database on heroku.
#SQLALCHEMY_DATABASE_URI= 'sqlite:///' + DATABASE_PATH previous database URI that stores database info locally. Refer back to this when developing locally
SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
