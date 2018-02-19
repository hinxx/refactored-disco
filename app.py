import os
from flask import Flask, render_template, request, jsonify
import datetime
import json
import time
from multiprocessing import Process, Value, Queue
import queue
import sqlite3

app = Flask(__name__)

@app.route('/')
def signUp():
    return render_template('index.html')

@app.route('/test1/<input1>/<input2>', methods=['GET'])
def test1(input1, input2):
#    print("Called test1()\n")
#    print("input1:", input1)
#    print("input2:", input2)

    datas = []
#     cons_con = sqlite3.connect('test.db')
    cons_cur = dbcon.cursor()
#     print("test1(): We have:", q.qsize())
    try:
        while True:
#            datas.append(q.get(False))
            cons_cur.execute("SELECT rowid,* FROM Frames ORDER BY rowid DESC LIMIT 10")
            rows = cons_cur.fetchall()
            for row in rows:
                datas.append(row)
            break
        
    except queue.Empty:
#         data = {'type': 'INVALID', 'stamp': str(datetime.datetime.now())}
        print("test1(): Getting %d frames" % len(datas))

    return jsonify(datas)

def producer(q):
    datas = []
    
#     prod_con = sqlite3.connect('test.db')
    prod_cur = dbcon.cursor()

    while True:
        print(str(datetime.datetime.now()), ": producing more data ..")
#        data = {'type': 'BPM', 'stamp': str(datetime.datetime.now())}
#        q.put(data)
        data = "INSERT INTO Frames VALUES('%s','%s')" % ('BPM', str(datetime.datetime.now()))
        prod_cur.execute(data)
        dbcon.commit()
#        print("producer(): We have generated:", q.qsize(), "::", data)
        print("producer(): We have generated:", data)
        
        time.sleep(1.3)
    
#     prod_con.close()

if __name__=="__main__":
    dbcon = sqlite3.connect('test.db')
#     cur = con.cursor()    
#     cur.execute('SELECT SQLITE_VERSION()')
#     data = cur.fetchone()
#     print("SQLite version: %s" % data)
#     del con
#     del cur
#     del data
    
    q = Queue()
    p = Process(target=producer, args=(q,))
    p.start()  
    # start web server and listen on all interfaces
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    p.join()
    dbcon.close()
