from flask import Flask, render_template, Response, request
import cv2
from modules.ship_detect import ShipDetector
import json


camserver = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
sd = ShipDetector()
data = {}
msg = {}
distance = {}
def gen_frames():  # generate frame by frame from camera
    while True: 
        ret,frame = camera.read()
        if not ret : break
        sd.detect(frame,data,distance)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@camserver.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@camserver.route('/recv',methods=['POST'])
def recv():
    global data 
    if request.method == 'POST':
        data = json.loads(request.get_json())
    return 'Success'

@camserver.route('/locate',methods=['POST'])
def recvLocation():
    global distance
    if request.method == 'POST':
        distance = json.loads(request.get_json())
    return 'Success'

import matplotlib.pyplot as plt
from modules.lidar import Lidar
ld = Lidar()

@camserver.route('/ladar')
def ladar():
    return Response(ld.run_lidar(), mimetype='multipart/x-mixed-replace; boundary=frame')

from modules.control import controler
@camserver.route('/control',methods=['POST'])
def antiTerrorControl():
    if request.method == 'POST':
        msg = json.loads(request.get_json())
        controler(data['status'])
    return 'Success'

# @camserver.route('/')
# def index():
#     """Video streaming home page."""
#     return render_template('index.html')


if __name__ == '__main__':
    camserver.run(debug=False, host='0.0.0.0',port=5050)
