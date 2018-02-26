# -*- coding: utf-8 -*-
"""
    WebPV
    ~~~~~

    An EPICS PV client application written with Flask and sqlite3.

    :copyright: © 2010 by the Pallets team.
    :copyright: © 2018 by the Hinko Kocevar.
    :license: BSD, see LICENSE for more details.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app


# create our blueprint :)
bp = Blueprint('webpv', __name__)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@bp.route('/', methods=['GET', 'POST'])
def show_entries():
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select title, text from entries order by id desc')
        entries = cur.fetchall()
        return render_template('show_entries.html', entries=entries)
    elif request.method == 'GET':
        db = get_db()
        cur = db.execute('SELECT rowid, * FROM Frames ORDER BY rowid DESC')
        stats = cur.fetchall()
        return render_template('stats.html', stats=stats)

@bp.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('webpv.show_entries'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('webpv.show_entries'))
    return render_template('login.html', error=error)


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('webpv.show_entries'))
