from http.server import HTTPServer, BaseHTTPRequestHandler

import json
from threading import Thread, Lock
import time

FILEDATA = dict()
STATE = {"mode":"menu"}
INTERNAL = {"termtime":0.0,"holdtime":0.0,"lastalive":0.0,"lastduration":0.0,"lastwait":0.0}
MUTEX = Lock()

def format_value(mins):
    m = int(mins)
    s = int((mins-m) * 60.0)
    m = str(m)
    s = str(s)
    if len(s) == 1:
        return m + ":0" + s
    else:
        return m + ":" + s

def do_input(message):
    if message[:3] == "go_":
        try:
            duration = float(message[3:])
        except:
            return
        INTERNAL["lastduration"] = duration
        STATE["mode"] = "running"
        INTERNAL["termtime"] = time.time() + (INTERNAL["lastduration"] * 60.0)
        STATE["value"] = format_value((INTERNAL["termtime"] - time.time()) / 60.0)
    elif message == "pause":
        STATE["mode"] = "pause"
        INTERNAL["holdtime"] = INTERNAL["termtime"] - time.time()
        STATE["value"] = format_value(INTERNAL["holdtime"] / 60.0)
    elif message == "unpause":
        STATE["mode"] = "running"
        INTERNAL["termtime"] = time.time() + INTERNAL["holdtime"]
        STATE["value"] = format_value((INTERNAL["termtime"] - time.time()) / 60.0)
    elif message == "stop":
        STATE["mode"] = "menu"

def do_alive():
    INTERNAL["lastalive"] = time.time()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global FILEDATA
        global STATE
        global MUTEX
        MUTEX.acquire()
        self.send_response(200)
        self.end_headers()
        if self.path in FILEDATA:
            self.wfile.write(FILEDATA[self.path])
        elif self.path == "/query":
            s = json.dumps(STATE)
            s = s.encode("UTF-8")
            self.wfile.write(s)
            if STATE["mode"] == "waiting":
                STATE["value"] = False
        elif self.path[:7] == "/input_":
            do_input(self.path[7:])
        elif self.path == "/alive":
            do_alive()
        else:
            self.wfile.write(b'')
        MUTEX.release()

def loadFile(filename,internal_name):
    global FILEDATA
    with open(filename,"rb") as file:
        data = file.read()
    FILEDATA[internal_name] = data

def load_FILEDATA():
    loadFile("index.html","/")
    loadFile("popup.html","/popup")
    loadFile("script.js","/script.js")

def update_value():
    global STATE
    global INTERNAL
    if STATE["mode"] == "running":
        STATE["value"] = (INTERNAL["termtime"] - time.time()) / 60.0
        if STATE["value"] <= 0.0:
            STATE["mode"] = "waiting"
            STATE["value"] = True
            INTERNAL["lastalive"] = time.time()
        else:
            STATE["value"] = format_value(STATE["value"])
    elif STATE["mode"] == "pause":
        STATE["value"] = format_value(INTERNAL["holdtime"] / 60.0)
    elif STATE["mode"] == "waiting":
        if time.time() - INTERNAL["lastalive"] >= 1.5:
            STATE["mode"] = "running"
            INTERNAL["termtime"] = time.time() + (INTERNAL["lastduration"] * 60.0)
            STATE["value"] = format_value((INTERNAL["termtime"] - time.time()) / 60.0)

def update_value_loop():
    global MUTEX
    while True:
        MUTEX.acquire()
        update_value()
        MUTEX.release()
        time.sleep(0.1)

def main():
    load_FILEDATA()
    th = Thread(None,update_value_loop)
    th.start()
    httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()

main()