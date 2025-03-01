import sqlite3
from datetime import datetime

import click 
from flask import current_app, g
'''Here, current_app points to the flask app handling an incoming request.
  g is an object unique to each request that allows for info to be reused.
'''

def get_db() -> sqlite3.Connection:
    '''Returns an sqlite database connection.
    
    If already present in the current request, return that db,
    otherwise one will be created and stored to the request. 
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None) -> None:
    '''Remove existing db connection from the request info object and close it.'''
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db() -> None:
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app) -> None:
    '''Register functions with the application instance.
    
    Necessary since we are using a factory and do not have 
    access to the app instance until it is created. 
    '''
    #Have flask call the close function as a 'destructor' of sorts
    app.teardown_appcontext(close_db) 
    #Adds this command as one that can be run from the flask cli
    app.cli.add_command(init_db_command)

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)