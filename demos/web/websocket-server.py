#!/usr/bin/env python2
import os
import sys
sys.path.insert(0,"./NFG")
import NFG
sys.path.insert(0,"./VideoCrop")
import VideoCrop as vc
fileDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(fileDir, "..", ".."))

import txaio
txaio.use_twisted()

from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from twisted.internet import task, defer
from twisted.internet.ssl import DefaultOpenSSLContextFactory

from twisted.python import log

import argparse
import cv2
import imagehash
import json
import numpy as np
import os
import StringIO
import urllib
import base64
import signal
import threading
import base64
import openface
import time
tls_crt = os.path.join(fileDir, 'tls', 'server.crt')
tls_key = os.path.join(fileDir, 'tls', 'server.key')

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=9000,
                    help='WebSocket Port')

args = parser.parse_args()
global crop
crop = threading.Thread
try:
    capture = cv2.VideoCapture(1)
    print('==========Video Access Complete========')
except:
    print('Failure')
    exit(1)

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    capture.release()
    crop.join()
signal.signal(signal.SIGINT, signal_handler)
def faceDetect(parent):
    face_cascade = cv2.CascadeClassifier('./demos/web/haarcascade_frontalface_default.xml')
    upper_cascade = cv2.CascadeClassifier('./demos/web/haarcascade_upperbody.xml')
    targetName = "Compare"
    absroute = "./demos/web/dataset/video/"
    absroute += targetName
    if not os.path.isdir(absroute):
        os.mkdir(absroute)
    
    framecnt = -1

    cnt = 0
    while True:
        ret, frame = capture.read()
	if not ret:
	    return
        #cnt = 0
        if framecnt != -1:
            framecnt += 1

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 2, 0, (30, 30))
        uppers = upper_cascade.detectMultiScale(gray, 1.3, 2, 0, (30,30))
	for (faceX, faceY, face_width, face_height) in faces:
            for(upperX, upperY, upper_width, upper_height) in uppers:
                if(upperX < faceX and upperX + upper_width > faceX + face_width and
                            upperY < faceY and upperY + upper_height > faceY + face_height):
                    img_trim = frame[upperY:upperY+ upper_height, upperX:upperX+upper_width]
                    midUpper = upperX + upper_width / 2
                    midFace = faceX + face_width / 2
                    print("detect!")
                    if framecnt == -1 :
                        outframe = img_trim
                        prev_point = [midUpper, midFace]
                        detect_path = './demos/web/dataset/detect/detect' + str(cnt) + '.jpg'
                        cnt+=1
                        temp = cv2.imwrite(detect_path, img_trim)
                        if temp:
                            parent.Compare(detect_path)
                        framecnt = 0
                        prev_point = [midUpper, midFace]
                    elif abs(midUpper - prev_point[0]) < 200 and abs(midFace - prev_point[1]) < 200 and framecnt < 300:
                        framecnt = 0
                    else :
                        detect_path = './demos/web/dataset/detect/detect' + str(cnt) + '.jpg'
                        cnt+=1
                        temp = cv2.imwrite(detect_path, img_trim)
                        framecnt = 0
                        if temp:
                            parent.Compare(detect_path)

                    #detect_path = './demos/web/dataset/detect/detect' + str(cnt) + '.jpg'
                    #temp = cv2.imwrite(detect_path, img_trim)
                    #if temp:
                    #    parent.Compare(detect_path)
                    #cnt+=1
#	if(cnt > 1):
#            parent.Compare(detect_path)

        ret, temp = cv2.imencode('.jpeg', frame)
        data = base64.b64encode(temp)
        length = len(data)
        message = {
	    'type' : 'VIDEO',
	    'length' : length,
	    'data' : data
        }
        parent.sendMessage(json.dumps(message))
        cv2.waitKey(80)

class OpenFaceServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        super(OpenFaceServerProtocol, self).__init__()
        self.images = {}
        self.training = True
        self.people = []
        self.svm = None
        self.t = None
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.training = True

    def onOpen(self):
        print("WebSocket connection open.")
        self.t = threading.Thread(target=faceDetect, args=(self,))
        self.t.daemon = True
        self.t.start()
    def onMessage(self, payload, isBinary):
        raw = payload.decode('utf8')
        msg = json.loads(raw)
        print("Received {} message of length {}.".format(
            msg['type'], len(raw)))
        if msg['type'] == "ALL_STATE":
            self.loadState(msg['images'], msg['training'], msg['people'])
        elif msg['type'] == 'COMPARE':
            print("COMPARE START")
            self.Compare("Compare.jpg");
        elif msg['type'] == "TRAIN":
            print("TRAIN START")
            train = threading.Thread(target = NFG.Train)
            train.start()
            msg = {
                    "type" : "TRAIN_RETURN"
                    };
            self.sendMessage(json.dumps(msg))
        elif msg['type'] == "VIDEOCROP":
            print("START THE CROP THE VIDEO")
            crop = threading.Thread(target=vc.VideoCrop, args=(msg['name'], msg['path']))
            crop.daemon = True
            crop.start()
        else:
            print("Warning: Unknown message type: {}".format(msg['type']))
    def Compare(self, _path):
        name, confidence, path = NFG.Compare(_path)
        msg = {
                "type" : "COMPARE_RETURN",
                "name" : name,
                "confidence" : confidence,
                "path" : path
                }
        self.sendMessage(json.dumps(msg))
    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

def main(reactor):
    log.startLogging(sys.stdout)
    factory = WebSocketServerFactory()
    factory.protocol = OpenFaceServerProtocol
    ctx_factory = DefaultOpenSSLContextFactory(tls_key, tls_crt)
    reactor.listenSSL(args.port, factory, ctx_factory)
    return defer.Deferred()

if __name__ == '__main__':
    task.react(main)
