import click
from flask.cli import with_appcontext

from project import db
from .models import Customer, User, Project, Panel


def create_tables():
    db.create_all()


