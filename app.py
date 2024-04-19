# Flask App
from flask import Flask, render_template, Response, request
import cv2
import numpy as np
import time  # Import time module for timing

app = Flask(__name__)

prev_light_status = None  # Variable to store previous light status
video_writer = None  # Variable to store video writer object
video_saved = False  # Variable to track if video is currently being saved
start_time = None  # Variable to store the start time of video recording

def check_light(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    avg_brightness = cv2.mean(hsv[:,:,2])[0]
    if avg_brightness < 100:
        return False
    else:
        return True

def process_frame(frame):
    # Add your video processing logic here
    # For example, you can apply filters, detect objects, etc.
    # Return the processed frame
    return frame

def start_video_writer(frame_width, frame_height):
    global video_writer, video_saved, start_time
    video_writer = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20, (frame_width, frame_height))
    video_saved = False
    start_time = time.time()  # Start the timer

def stop_video_writer():
    global video_writer, video_saved, start_time
    if video_writer is not None:
        video_writer.release()
        video_saved = True
        print("Video saved successfully.")
    start_time = None  # Reset start time when video recording stops

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['POST'])
def video_feed():
    global prev_light_status, video_writer, start_time

    # Get the frame sent from the client
    frame = request.files['frame'].read()

    # Convert frame to numpy array
    nparr = np.frombuffer(frame, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    current_light_status = check_light(frame)

    # Check if the current light status differs from the previous one
    if current_light_status != prev_light_status:
        if current_light_status:
            print("Enough light. Processing video...")
            start_video_writer(frame.shape[1], frame.shape[0])
        else:
            print("Not enough light. Please increase light.")
    
        
        # Update the previous light status
        prev_light_status = current_light_status

    if current_light_status and video_writer is not None:
        # Check if 60 seconds have passed since the start of video recording
        if time.time() - start_time <= 60:
            processed_frame = process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()

            # Write frame to video file
            video_writer.write(processed_frame)

            return Response(b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n',
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            print("Video recording stopped. Maximum duration reached.")
            stop_video_writer()
            return Response(status=200)
    else:
        return Response(status=500)

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global video_writer
    stop_video_writer()
    return 'Recording stopped.'

if __name__ == "__main__":
    app.run(debug=True)
