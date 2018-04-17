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
import pickle
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
        
        if 'UntilWhen' in req and len(req['UntilWhen']):
            untilTime = datetime.datetime.strptime(req['UntilWhen'], '%Y-%m-%d %H:%M:%S')
            print('user supplied UntilWhen: ', untilTime)
        else:
            untilTime = now
            print('using now() for UntilWhen: ', untilTime)
        
        if 'FromWhen' in req and len(req['FromWhen']):
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
                entry = []
                # print('opening binary file %s ..' % row[3])
                with open(row[3], 'rb') as fp:
                    entry = pickle.load(fp)
                fp.close()
                # print('binary file %s contents:\n%s' % (row[3], entry.tolist()))
                
                r = {
                    'Rowid': row[0],
                    'PVName': row[1],
                    'TimeStamp': row[2],
                    'PVData': entry.tolist()
                    }
                datas.append(r)
        return jsonify(datas)

    elif request.method == 'GET':
        print("GET request:", request)

    return json.dumps(request.get_json())
