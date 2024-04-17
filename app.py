from flask import Flask, render_template, Response
import cv2
import time

app = Flask(__name__)

def check_light(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    avg_brightness = cv2.mean(hsv[:,:,2])[0]
    if avg_brightness < 100:
        return False
    else:
        return True

def generate_frames():
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('videos/output.avi', fourcc, 20.0, (640, 480))
    
    light_status = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_light_status = check_light(frame)
        
        if light_status is None:
            light_status = current_light_status
            if light_status:
                print("Enough light. Capturing video...")
        elif light_status != current_light_status:
            light_status = current_light_status
            if light_status:
                print("Enough light. Capturing video...")
            else:
                print("Not enough light. Please increase light.")
        
        if light_status:
            out.write(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            if time.time() - start_time > 60:
                break
                
    out.release()
    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)