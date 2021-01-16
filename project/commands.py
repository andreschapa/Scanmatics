import click
from flask.cli import with_appcontext

from project import db
from .models import Customer, User, Project, Panel

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()