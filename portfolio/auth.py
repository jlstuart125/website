"""
This module contains the blueprint for authentication functions.
"""

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from portfolio.db import get_db


'''               __ the name of the blueprint.
                 |       ___ tells the blueprint where it is defined.  
                 |      |        
'''
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register() -> str:
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login() -> str:
    """Define the 'login' view.

    Will check the database to authenticate the user. 
    Stores the user's id in the session and makes it available
    on subsequent requests. 
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            #session is a dict that stores data across requests.
            session.clear()
            #the user's id is stored in a new session, stored in the browser as a cookie
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user() -> None:
    '''Checks if a user id is stored in the session and retrieves their info from db.'''
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(

            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    """I wanted to put in a return type but was unsure how to resolve Response
    in this context.
    """
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    '''Returns a new view function that wraps the original view it was applied
    to and redirects to the login page otherwise.
    
    If a user is loaded, the original view is called and continues normally.
    '''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            '''Here, url_for is returning the URL to the view based on its
            name - referred to as its 'endpoint' which is the same as the name
            of the view function by default.
            When using a blueprint, the name of the blueprint is prepended to 
            the name of the function, hence the 'auth.'
            '''
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

