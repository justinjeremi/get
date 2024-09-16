import io
import time
from picamera2 import Picamera2, Preview
from flask import Flask, Response

app = Flask(__name__)

# Initialize Picamera2
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

def generate_frames():
    # Create an in-memory stream
    stream = io.BytesIO()
    
    while True:
        # Capture a frame to the in-memory stream
        camera.capture(stream, format='jpeg', use_video_port=True)
        
        # Rewind the stream to the beginning
        stream.seek(0)
        frame = stream.read()
        
        # Reset the stream for the next frame
        stream.seek(0)
        stream.truncate()
        
        # Yield the frame in a format suitable for MJPEG streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Live Webcam Feed</title>
        </head>
        <body>
            <h1>Live Webcam Feed</h1>
            <img src="/video_feed" style="width:100%; max-width:640px;" />
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
