from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np

app = Flask(__name__)

prev_light_status = None  # Variable to store previous light status
recording = False
frames = []

def check_light(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    avg_brightness = cv2.mean(hsv[:,:,2])[0]
    if avg_brightness < 100:
        return False
    else:
        return True

def save_video():
    global frames
    if len(frames) > 0:
        height, width, _ = frames[0].shape
        out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 5.0, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()
        frames = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['POST'])
def video_feed():
    global prev_light_status, recording, frames  # Access global variables

    # Get the frame sent from the client
    frame = request.files['frame'].read()

    # Convert frame to numpy array
    nparr = np.frombuffer(frame, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    current_light_status = check_light(frame)

    # Check if the current light status differs from the previous one
    if current_light_status != prev_light_status:
        if current_light_status:
            print('Enough light. Processing video...')
            response = jsonify({'message': 'Enough light. Processing video...'})
        else:
            print('Not enough light. Please increase light.')
            response = jsonify({'message': 'Not enough light. Please increase light.'})
        
        # Update the previous light status
        prev_light_status = current_light_status
        return response

    if current_light_status:
        if recording:
            # Resize frame to 720p
            frame = cv2.resize(frame, (1280, 720))
            frames.append(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            return Response(b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n',
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return jsonify({'message': 'Recording not started.'})
    else:
        return jsonify({'error': 'Not enough light. Recording paused.'}), 500

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording
    recording = True
    return jsonify({'message': 'Recording started.'})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording
    recording = False
    save_video()
    return jsonify({'message': 'Recording stopped. Video saved.'})

if __name__ == "__main__":
    app.run(debug=True)
