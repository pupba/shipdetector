from flask import Flask, render_template, Response
import cv2
from modules.ship_detect import ShipDetector

camserver = Flask(__name__)

camera = cv2.VideoCapture(0)
sd = ShipDetector()

def gen_frames():  # generate frame by frame from camera
    
    while True:
        ret,frame = camera.read()
        if not ret : break
        sd.detect(frame)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@camserver.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@camserver.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    camserver.run(debug=True)