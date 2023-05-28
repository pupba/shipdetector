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
def gen_frames():  # generate frame by frame from camera
    while True: 
        ret,frame = camera.read()
        if not ret : break
        sd.detect(frame,data)
        
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

from io import BytesIO
import matplotlib.pyplot as plt
# 애니메이션을 생성하는 함수
def generate_animation():
    fig, ax = plt.subplots()

    # 애니메이션 프레임을 생성하는 함수
    def animate(frame):
        ax.clear()
        ax.plot([1, 2, 3, 4], [frame, frame, frame, frame])  # 예시: 간단한 그래프

    # 애니메이션 프레임을 바이트 스트림으로 변환
    def generate_frames():
        a = 0
        while True :
            # 레이더
            animate(a%10)
            a+=1
            # 그래프를 이미지로 변환
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            frame_bytes = buffer.getvalue()

            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + frame_bytes + b'\r\n')

    # 애니메이션 프레임을 스트리밍하는 Response 객체 반환
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@camserver.route('/ladar')
def ladar():
    return generate_animation()

from modules.control import controler
@camserver.route('/control',methods=['POST'])
def antiTerrorControl():
    if request.method == 'POST':
        data = json.loads(request.get_json())
        controler(data['status'])
    return 'Success'

# @camserver.route('/')
# def index():
#     """Video streaming home page."""
#     return render_template('index.html')


if __name__ == '__main__':
    camserver.run(debug=False, host='0.0.0.0',port=5050)