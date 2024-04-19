from flask import Flask, render_template, Response, request
import cv2
import numpy as np

app = Flask(__name__)

prev_light_status = None  

def check_light(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    avg_brightness = cv2.mean(hsv[:,:,2])[0]
    if avg_brightness < 100:
        return False
    else:
        return True

def process_frame(frame):
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['POST'])
def video_feed():
    global prev_light_status  

    frame = request.files['frame'].read()

    nparr = np.frombuffer(frame, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    current_light_status = check_light(frame)

    if current_light_status != prev_light_status:
        if current_light_status:
            print("Enough light. Processing video...")
        else:
            print("Not enough light. Please increase light.")
        
        prev_light_status = current_light_status

    if current_light_status:
        processed_frame = process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()
        return Response(b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n',
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(status=500)

if __name__ == "__main__":
    app.run(debug=True)
