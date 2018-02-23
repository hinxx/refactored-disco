import os
from flask import Flask, render_template, request, jsonify
import datetime
import json
import time
from multiprocessing import Process
import sqlite3
import numpy as np
import array

app = Flask(__name__)

@app.route('/')
def signUp():
    return render_template('index.html')

@app.route('/test1/id/<id>', methods=['GET'])
#@app.route('/test1/diag/<diag>', methods=['GET'])
#@app.route('/test1/diag/<diag>/pv/<pv>', methods=['GET'])
def test1(id):
    print("Called test1(): ID=", id, "\n")

# DEBUG
#     print(dir(request))
#     print(request.args)
#     print(request.view_args)
#     #print(request.headers)
#     print(request.query_string)
#     print(request.remote_addr)
#     print(request.path)
# 
#     cnt = 10
#     searchword = request.args.get('cnt', '')
#     print("searchword:", searchword)
# DEBUG

    datas = []
    cons_cur = dbcon.cursor()
    
    cons_cur.execute("SELECT rowid,* FROM Frames ORDER BY rowid DESC LIMIT 10")
    rows = cons_cur.fetchall()
    for row in rows:
        r = {
            'id': row[0],
            'type': row[1],
            'stamp': row[2],
            'signal': memoryview(row[3]).tolist()
            }
        datas.append(r)
       
    return jsonify(datas)

def producer():
    prod_cur = dbcon.cursor()

    while True:
        print(str(datetime.datetime.now()), ": producing more data ..")

        # generate noisy trace
        pure = np.linspace(-1, 1, 100)
        noise = np.random.normal(0, 1, pure.shape)
        signal = pure + noise
        ablob = sqlite3.Binary(signal)
        
        sql = '''INSERT INTO Frames (type, stamp, signal) VALUES(?, ?, ?);'''
        prod_cur.execute(sql, ['BPM', str(datetime.datetime.now()), ablob]) 
        dbcon.commit()
        id = prod_cur.lastrowid
        print("producer(): We have generated data with ROW ID:", id)
        
        time.sleep(1.3)

if __name__=="__main__":
    dbcon = sqlite3.connect('test.db')
    p = Process(target=producer)
    p.start()  
    # start web server and listen on all interfaces
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    p.join()
    dbcon.close()
