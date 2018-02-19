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
    print("input1:", input1)
    print("input2:", input2)

    datas = []
    cons_cur = dbcon.cursor()
    id = cons_cur.lastrowid

    print("test1(): We have:", id)
    cons_cur.execute("SELECT rowid,* FROM Frames ORDER BY rowid DESC LIMIT 10")
    rows = cons_cur.fetchall()
    for row in rows:
        datas.append(row)
        
    return jsonify(datas)

def producer():
    prod_cur = dbcon.cursor()

    while True:
        print(str(datetime.datetime.now()), ": producing more data ..")
        data = "INSERT INTO Frames VALUES('%s','%s')" % ('BPM', str(datetime.datetime.now()))
        prod_cur.execute(data)
        dbcon.commit()
        id = prod_cur.lastrowid
        print("producer(): We have generated:", data, 'with ROW ID: ', id)
        
        time.sleep(1.3)

if __name__=="__main__":
    dbcon = sqlite3.connect('test.db')
    p = Process(target=producer)
    p.start()  
    # start web server and listen on all interfaces
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    p.join()
    dbcon.close()
