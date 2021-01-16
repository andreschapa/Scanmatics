import click
from flask.cli import with_appcontext

from project import db
from .models import Customer, User, Project, Panel


def create_tables():
    db.create_all()

def init_app(app):
    for command in [create_tables]:
        app.cli.add_command(app.cli.command()(command))



