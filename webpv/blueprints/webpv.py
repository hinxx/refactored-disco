# -*- coding: utf-8 -*-
"""
    WebPV
    ~~~~~

    An EPICS PV client application written with Flask and sqlite3.

    :copyright: © 2010 by the Pallets team.
    :copyright: © 2018 by the Hinko Kocevar.
    :license: BSD, see LICENSE for more details.
"""

import json
import array
import datetime
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app, jsonify


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
    print("request method:", request)
    if request.method == 'POST':
        print("POST request content_length:", request.content_length)
        print("POST request is_json:", request.is_json)
#        print("POST request:", request)
#        print("POST args:", request.args.to_dict())
#        print("POST view_args:", request.view_args)
#        print("POST form:", request.form.to_dict())
#        print("POST data:", request.data)

        if request.content_length == 0:
          return '{ "Error": "Missing JSON encoded request"}'
       
        print("POST request json:", request.get_json())
        req = request.get_json()

        if 'PVs' not in req:
          return '{ "Error": "Missing JSON encoded \'PVs\' in request"}'
          
        now = datetime.datetime.now()

        # with microseconds    : datetime.datetime.strptime('2018-02-28 11:27:31.061988', '%Y-%m-%d %H:%M:%S.%f')
        # without microseconds : datetime.datetime.strptime('2018-02-28 11:27:31', '%Y-%m-%d %H:%M:%S')
        
        if 'UntilWhen' in req:
            untilTime = datetime.datetime.strptime(req['UntilWhen'], '%Y-%m-%d %H:%M:%S')
            print('user supplied UntilWhen: ', untilTime)
        else:
            untilTime = now
            print('using now() for UntilWhen: ', untilTime)
        
        if 'FromWhen' in req:
            fromTime = datetime.datetime.strptime(req['FromWhen'], '%Y-%m-%d %H:%M:%S')
            print('user supplied FromWhen: ', fromTime)
        else:
            fromTime = untilTime - datetime.timedelta(seconds=50)
            print('using UntilTime - 5s for FromWhen: ', fromTime)
            
        print('calculated time frame\nFROM:  ', fromTime, '\nUNTIL: ', untilTime, '\nTOTAL: ', untilTime - fromTime)
        
        db = get_db()
        datas = []
        for pv in req['PVs']:
            sql = 'SELECT rowid,* FROM Frames ' \
                'WHERE PVName = ? ' \
                'AND TimeStamp >= ? ' \
                'AND TimeStamp <= ? '\
                'ORDER BY rowid'
            cur = db.execute(sql, [pv, fromTime, untilTime])
            rows = cur.fetchall()
            for row in rows:
                # make sure that floats are properly decoded from BLOB!
                a = array.array('f')
                a.frombytes(row[3])
                r = {
                    'Rowid': row[0],
                    'PVName': row[1],
                    'TimeStamp': row[2],
                    'PVData': a.tolist()
                    }
                datas.append(r)
        return jsonify(datas)

    elif request.method == 'GET':
        print("GET request:", request)
#         db = get_db()
#         cur = db.execute('SELECT rowid, * FROM Frames ORDER BY rowid DESC')
#         stats = cur.fetchall()
#         return render_template('stats.html', stats=stats)
#     return "{ 'DODO': 'bird' }"
#     return '{ "DODO": "bird" }'
    return json.dumps(request.get_json())

# @bp.route('/add', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     db = get_db()
#     db.execute('insert into entries (title, text) values (?, ?)',
#                [request.form['title'], request.form['text']])
#     db.commit()
#     flash('New entry was successfully posted')
#     return redirect(url_for('webpv.show_entries'))
# 
# 
# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != current_app.config['USERNAME']:
#             error = 'Invalid username'
#         elif request.form['password'] != current_app.config['PASSWORD']:
#             error = 'Invalid password'
#         else:
#             session['logged_in'] = True
#             flash('You were logged in')
#             return redirect(url_for('webpv.show_entries'))
#     return render_template('login.html', error=error)
# 
# 
# @bp.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     flash('You were logged out')
#     return redirect(url_for('webpv.show_entries'))
