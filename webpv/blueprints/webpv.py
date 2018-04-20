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
import time
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app, jsonify, json, Response, after_this_request
import gzip
from io import BytesIO

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
    # test adding a header after response is already built..
    @after_this_request
    def add_header(response):
        response.headers['X-Foo'] = 'Parachute'
        return response

    # gzip compress the response
    # XXX: this makes response time 10x longer
    # XXX: this makes response length at least 1/2 smaller
    @after_this_request
    def zipper(response):
        # use compression only if request requested it!
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' not in accept_encoding.lower():
            return response

        response.direct_passthrough = False

        if (response.status_code < 200 or
            response.status_code >= 300 or
            'Content-Encoding' in response.headers):
            return response
#         gzip_buffer = IO()
        gzip_buffer = BytesIO()
        gzip_file = gzip.GzipFile(mode='wb', fileobj=gzip_buffer)
        gzip_file.write(response.data)
        # remove spaces from JSON
#         gzip_file.write(response.data.replace(' ', ''))
        gzip_file.close()

        response.data = gzip_buffer.getvalue()
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Vary'] = 'Accept-Encoding'
        response.headers['Content-Length'] = len(response.data)

        return response


    print("request method:", request.method)
    if request.method == 'POST':
        rss = datetime.datetime.now()

        print("POST request content_length:", request.content_length)
        print("POST request is_json:", request.is_json)
        print("POST request is_xhr:", request.is_xhr)
        print("POST request header:", request.headers)
#         print("POST request:", request)
#         print("POST args:", request.args.to_dict())
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
            fromTime = untilTime - datetime.timedelta(seconds=300)
            print('using UntilTime - 300s for FromWhen: ', fromTime)
            
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
            print('got %d rows from DB' % len(rows))
            for row in rows:
#                 print('>> row %d: %s' % (row[0], row[2]))
                
#                 entry = array.array('H')
                # print('opening binary file %s ..' % row[3])
#                 with open(row[3], 'rb') as fp:
#                     entry = pickle.load(fp)
#                 fp.close()
#                 with open(row[3], 'rb') as fp:
#                     entry.fromfile(fp, 300)
#                 fp.close()
#                 print('started JSON load: %s' % (datetime.datetime.now()))
#                 ss = datetime.datetime.now()
                entry = []
                with open(row[3], 'r') as fp:
                    entry = json.load(fp)
                fp.close()
#                 print('ended JSON load: %s' % (datetime.datetime.now()))
#                 ee = datetime.datetime.now()
#                 print('JSON load took %s' % str(ee-ss))
                # print('binary file %s contents:\n%s' % (row[3], entry.tolist()))
                
                r = {
                    'Rowid': row[0],
                    'PVName': row[1],
                    'TimeStamp': row[2],
#                     'PVData': entry.tolist()
                    'PVData': entry
                    }
                datas.append(r)
                
#         datas = ['{"nothing": "nothing!"']
#         return jsonify(datas)
        
        ree = datetime.datetime.now()
#         datas = jsonify(datas)
        print('request handle took %s (sending %d bytes)' % (str(ree-rss), len(json.dumps(datas))))
        jdata = json.dumps(datas)
#         jdata = json.dumps(datas).replace(' ', '')
#         return jsonify(datas)
        print('JSONified: %s' % jdata[0:70])
#         return Response(jdata, status=200, mimetype='application/json')
        response = Response(jdata, status=200, mimetype='application/json')
        response = add_header(response)
        response = zipper(response)
        return response

    elif request.method == 'GET':
        print("GET request:", request)

    return json.dumps(request.get_json())
