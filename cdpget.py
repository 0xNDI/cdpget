#!/usr/bin/env python3

import io
import sys
import json
import requests
import websocket
import base64
import PyPDF2
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="The remote file to print")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
parser.add_argument("-t", "--target", type=str, default="127.0.0.1", help="The target to connect to (default: 127.0.0.1)")
parser.add_argument("-p", "--port", type=int, default=9222, help="The port to use (default: 9222)")
args = parser.parse_args()

response = requests.get(f"http://{args.target}:{args.port}/json")
tabs = response.json()

def recv_until(reqid):
    while True:
        result = json.loads(ws.recv())
        if "id" in result and reqid == result["id"]:
            return result
        
def vprint(*pargs, **kwargs):
    if args.verbose:
        print(*pargs, **kwargs)

web_socket_debugger_url = tabs[0]["webSocketDebuggerUrl"]

vprint(f"Connect to url: {web_socket_debugger_url}")

ws = websocket.create_connection(web_socket_debugger_url, suppress_origin=True)
ws.settimeout(5)

command = json.dumps({
    "id": 1,
    "method": "Target.createTarget",
    "params": {
        "url": f"file://{args.file}"
    }})

ws.send(command)
result = recv_until(1)
target_id = result["result"]["targetId"]
vprint(f"Target id: {target_id}")

command = json.dumps({
    "id": 2,
    "method": "Target.attachToTarget",
    "params": {
        "targetId": target_id
    }})

ws.send(command)
result = recv_until(2)

session_id = result["result"]["sessionId"]
vprint(f"Session id: {session_id}")

command = json.dumps({
    "id": 3,
    "sessionId": session_id,
    "method": "Page.printToPDF"
    })
while True:
    ws.send(command)
    try:
        result = recv_until(3)
    except websocket._exceptions.WebSocketTimeoutException:
        sys.stderr.write("Timeout, retrying...\n")
        continue

    if "result" in result and "data" in result["result"]:
        vprint("PDF file received\n")
        
        pdfbytes=base64.b64decode(result["result"]["data"])
        file_like = io.BytesIO(pdfbytes)
        reader = PyPDF2.PdfReader(file_like)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        if len(text) == 0:
            sys.stderr.write("Got empty pdf\n")
            break
        else:
            print(text)
            break
    else:
        sys.stderr.write("Error reading file\n")
        break

command = json.dumps({
    "id": 4,
    "sessionId": session_id,
    "method": "Target.closeTarget",
    "params": {
        "targetId": target_id
    }
})

ws.send(command)
recv_until(4)
ws.close()