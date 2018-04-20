# -*- coding: utf-8 -*-
"""
    WebPV
    ~~~~~

    An EPICS PV client application written with Flask and sqlite3.

    :copyright: © 2010 by the Pallets team.
    :copyright: © 2018 by the Hinko Kocevar.
    :license: BSD, see LICENSE for more details.
"""

import os
from multiprocessing import Process
import datetime
import time
import sqlite3
import array
import pickle
import json
import numpy as np
from flask import Flask, g
from flask_cors import CORS
from werkzeug.utils import find_modules, import_string
from webpv.blueprints.webpv import init_db

g_producer = None

def create_app(config=None):
    app = Flask('webpv')
    CORS(app)

    app.config.update(dict(
        DATABASE=os.path.join(app.root_path, 'webpv.db'),
        DEBUG=True,
        SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
        USERNAME='admin',
        PASSWORD='default',
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=False
    ))
    app.config.update(config or {})
    app.config.from_envvar('WEBPV_SETTINGS', silent=True)

    register_blueprints(app)
    register_cli(app)
    register_teardowns(app)
#     register_producers(app)
    app.before_first_request(register_producer)

#     import pdb; pdb.set_trace();
    
    print('this is app.cli: %s' % str(app.cli.name))
    
    return app


def register_blueprints(app):
    """Register all blueprint modules

    Reference: Armin Ronacher, "Flask for Fun and for Profit" PyBay 2016.
    """
    for name in find_modules('webpv.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None


def register_cli(app):
    @app.cli.command('initdb')
    def initdb_command():
        """Creates the database tables."""
        init_db()
        print('Initialized the database.')


def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        """Closes the database again at the end of the request."""
        print("XXX: Calling close_db()..")
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()
#     @app.teardown_appcontext
#     def stop_producer(error):
#         """Closes the database again at the end of the request."""
#         print("XXX: Calling stop_producer()..")
#         if hasattr(g, 'producer'):
#             g.producer.join()


# def register_producers(app):
#     """Register all producer modules"""
#     
#     print('calling register_producers() ..')
#     
#     with app.app_context():
#         if not hasattr(g, 'producer'):
#             g.producer = Process(target=producer)
#             # XXX: This messesup the CLI initdb call!!!
#             g.producer.start()

def register_producer():
    print('calling register_producer() ..')
#     with app.app_context():
#         if not hasattr(g, 'producer'):
#             g.producer = Process(target=producer)
#             # XXX: This messesup the CLI initdb call!!!
#             g.producer.start()
    
    global g_producer
    if not g_producer:
        g_producer = Process(target=producer)
        g_producer.start()

def producer():
    print('>> producer() called!!!!')
    
    dbcon = sqlite3.connect('webpv/webpv.db', timeout=10)
    prod_cur = dbcon.cursor()

    if not os.path.isdir('storage'):
        os.mkdir('storage')

    while True:
        print(str(datetime.datetime.now()), ": producing more data ..")

        dt = datetime.datetime.now()
        # create 'YYYYmmdd_HHMMSS_uuuuuu' filename format from current date&time w/ microseconds
        file_name = dt.strftime("%Y%m%d_%H%M%S_%f.bin")
        sql = '''INSERT INTO Frames (PVName, TimeStamp, DataPath) VALUES(?, ?, ?);'''
        
        # generate noisy trace
        pure = np.linspace(-1, 1, 300)
#        for pv in [
#          'MEBT-010:PBI-BPM-001:Xpos', 'MEBT-010:PBI-BPM-001:Ypos', 'MEBT-010:PBI-BPM-001:Phase',
#          'MEBT-010:PBI-BPM-002:Xpos', 'MEBT-010:PBI-BPM-002:Ypos', 'MEBT-010:PBI-BPM-002:Phase',
#          'MEBT-010:PBI-BPM-003:Xpos', 'MEBT-010:PBI-BPM-003:Ypos', 'MEBT-010:PBI-BPM-003:Phase',]:
        for pv in ['MEBT-010:PBI-BPM-001:Xpos']:
            noise = np.random.normal(0, 1, pure.shape)
            signal = pure + noise
            # save to path: pv/filename
            path = os.path.join('storage', pv)
            if not os.path.isdir(path):
                os.mkdir(path)
            path = os.path.join('storage', pv, file_name)
#             entry = array.array('f')
#             entry.fromlist(signal.tolist())
#             with open(path, 'wb') as fp:
#                 pickle.dump(entry, fp)
#             fp.close()

            entry = signal.tolist()
            with open(path, 'w') as fp:
                json.dump(entry, fp)
            fp.close()

            # insert the path into the DB
            prod_cur.execute(sql, [pv, dt, path])

        # generate noisy intensity graph (aka image)
        pure = np.linspace(30000, 40000, 10000)
#        for pv in [
#          'MEBT-010:PBI-BPM-001:Img',
#          'MEBT-010:PBI-BPM-002:Img',
#          'MEBT-010:PBI-BPM-003:Img',]:
        for pv in ['MEBT-010:PBI-BPM-001:Img']:
#             signal = pure
#             noise = np.random.normal(1000, 5000, pure.shape)
            noise = np.random.randint(1111, 11111, pure.shape)
            signal = pure + noise
            # save to path: pv/filename
            path = os.path.join('storage', pv)
            if not os.path.isdir(path):
                os.mkdir(path)
            path = os.path.join('storage', pv, file_name)
#             entry = array.array('H')
#             entry.fromlist(signal.astype(np.uint16).tolist())
            
#             with open(path, 'wb') as fp:
#                 pickle.dump(entry, fp)
#             fp.close()
#             with open(path, 'wb') as fp:
#                 entry.tofile(fp)
#             fp.close()

            entry = signal.astype(np.uint16).tolist()
#             print('entry is %s, len %d' % (type(entry), len(entry)))
            with open(path, 'w') as fp:
                json.dump(entry, fp)
            fp.close()
            
            # insert the path into the DB
            prod_cur.execute(sql, [pv, dt, path])
        
        dbcon.commit()
        id = prod_cur.lastrowid
        print("producer(): We have generated data with ROW ID:", id)
        
        time.sleep(10.0)

