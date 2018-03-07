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
import numpy as np
from flask import Flask, g
from flask_cors import CORS
from werkzeug.utils import find_modules, import_string
from webpv.blueprints.webpv import init_db


def create_app(config=None):
    app = Flask('webpv')
    CORS(app)

    app.config.update(dict(
        DATABASE=os.path.join(app.root_path, 'webpv.db'),
        DEBUG=True,
        SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
        USERNAME='admin',
        PASSWORD='default'
    ))
    app.config.update(config or {})
    app.config.from_envvar('WEBPV_SETTINGS', silent=True)

    register_blueprints(app)
    register_cli(app)
    register_teardowns(app)
    register_producers(app)

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

def register_producers(app):
    """Register all producer modules"""
    with app.app_context():
        if not hasattr(g, 'producer'):
            g.producer = Process(target=producer)
            # XXX: This messesup the CLI initdb call!!!
            g.producer.start()

def producer():
    dbcon = sqlite3.connect('webpv/webpv.db')
    prod_cur = dbcon.cursor()

    while True:
        print(str(datetime.datetime.now()), ": producing more data ..")

        dt = datetime.datetime.now()

        # generate noisy trace
        pure = np.linspace(-1, 1, 300)

        sql = '''INSERT INTO Frames (PVName, TimeStamp, PVData) VALUES(?, ?, ?);'''
       
        # XXX: make sure floats are properly encoded for BLOB!!!
        for pv in [
          'MEBT-010:PBI-BPM-010:Xpos', 'MEBT-010:PBI-BPM-010:Ypos', 'MEBT-010:PBI-BPM-010:Phase',
          'MEBT-010:PBI-BPM-020:Xpos', 'MEBT-010:PBI-BPM-020:Ypos', 'MEBT-010:PBI-BPM-020:Phase',
          'MEBT-010:PBI-BPM-030:Xpos', 'MEBT-010:PBI-BPM-030:Ypos', 'MEBT-010:PBI-BPM-030:Phase',]:
          noise = np.random.normal(0, 1, pure.shape)
          signal = pure + noise
          a = array.array('f')
          a.fromlist(signal.tolist())
          ablob = sqlite3.Binary(a)
          # print("size of signal", len(signal))
          prod_cur.execute(sql, [pv, dt, ablob])

#        noise = np.random.normal(0, 1, pure.shape)
#        signalY = pure + noise
#        a = array.array('f')
#        a.fromlist(signalY.tolist())
#        ablobY = sqlite3.Binary(a)
#
#        noise = np.random.normal(0, 1, pure.shape)
#        signalP = pure + noise
#        a = array.array('f')
#        a.fromlist(signalP.tolist())
#        ablobP = sqlite3.Binary(a)
#        
#         print("size of signalX:", len(signalX))
#         print("size of signalY:", len(signalY))
#         print("size of signalP:", len(signalP))
#        
#        sql = '''INSERT INTO Frames (PVName, TimeStamp, PVData) VALUES(?, ?, ?);'''
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-010:Xpos', dt, ablobX])
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-010:Ypos', str(dt), ablobY])
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-010:Phase', str(dt), ablobP])
#
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-020:Xpos', dt, ablobX])
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-020:Ypos', str(dt), ablobY])
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-020:Phase', str(dt), ablobP])
#        
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-030:Xpos', dt, ablobX])
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-030:Ypos', str(dt), ablobY])
#        prod_cur.execute(sql, ['MEBT-010:PBI-BPM-030:Phase', str(dt), ablobP])
        
        dbcon.commit()
        id = prod_cur.lastrowid
        print("producer(): We have generated data with ROW ID:", id)
        
        time.sleep(3.0)

