import os
from flask import Flask, render_template, request, jsonify
import datetime
import json
import time
from multiprocessing import Process, Value, Queue
import queue

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
    print("test1(): We have:", q.qsize())
    try:
        while True:
            datas.append(q.get(False))
    except queue.Empty:
#         data = {'type': 'INVALID', 'stamp': str(datetime.datetime.now())}
        print("test1(): Getting %d dicts" % len(datas))

    return jsonify(datas)

def producer(q):
    datas = []
    while True:
        print(str(datetime.datetime.now()), ": producing more data ..")
        data = {'type': 'BPM', 'stamp': str(datetime.datetime.now())}
        q.put(data)
        print("producer(): We have generated:", q.qsize(), "::", data)
        
        time.sleep(1.3)

if __name__=="__main__":
    q = Queue()
    p = Process(target=producer, args=(q,))
    p.start()  
    # start web server and listen on all interfaces
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    p.join()
