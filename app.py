from flask import Flask, render_template, Response
from glitch_this import ImageGlitcher
import pyaudio as pa
import numpy as np
import aubio
import cv2
import shutil
import os
import random

app = Flask(__name__)

camera = cv2.VideoCapture(0)
glitcher = ImageGlitcher()

# SETUP pyaudio constants
CHUNK = 1024
FORMAT = pa.paFloat32
CHANNELS = 1
RATE = 44100
# pyaudio object
p = pa.PyAudio()
stream = p.open( 
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# Aubio's pitch detection.
pDetection = aubio.pitch("default", 2048,
                         2048//2, 44100)
# Set unit.
pDetection.set_unit("Hz")
pDetection.set_silence(-40)

# Different image filters
def apply_invert(frame):
    return cv2.bitwise_not(frame)

def gen_frames():
    # Remove remaining frames from previous runs
    tmp_path = './temp'
    gtmp_path = './glitched_temp'
    try:
        shutil.rmtree(tmp_path)
        shutil.rmtree(gtmp_path)
    except OSError as e:
        print("Error deleting folders")

    # Create empty folders
    os.makedirs("./temp")
    os.makedirs("./glitched_temp")
    
    count = 1
    while True:
        # listen to audio spectrum to determine glitch intensity
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.fromstring(data, dtype=aubio.float_type)
        pitch = pDetection(samples)[0]
        # print(f"pitch: {pitch}")
        # Compute the energy (volume) of the
        # current frame.
        volume = np.sum(samples**2)/len(samples)
        # Format the volume output so that at most
        # it has six decimal numbers.
        # volume = "{:.6f}".format(volume)
        # print(f"volume: {volume}")

        # glitch intensity varies based on audio pitch
        largest_hz_i_can_make = 850
        intensity = ((pitch + volume * (10**5)) / largest_hz_i_can_make) * 10
        if intensity < 0.1:
            intensity = 0.1
        elif intensity > 10:
            intensity = 10

        success, frame = camera.read()  # read the camera frame
        frame = cv2.flip(frame, 1)  # flip image on the x-axis
        if intensity > 2 and bool(random.getrandbits(1)):
            frame = apply_invert(frame)
        # save og frame from live webcam stream as image
        ffp = f"./temp/frame{count}.jpg"
        cv2.imwrite(ffp, frame)
        
        has_scanlines = intensity > 0.1 and bool(random.getrandbits(1))
        # glitch frame
        glitched_frame = glitcher.glitch_image(ffp, intensity, color_offset=True, scan_lines=has_scanlines)
        # save glitched frame as image
        gfp = f"./glitched_temp/glitched{count}.jpg"
        glitched_frame.save(gfp)
        # retrieve glitched frame from saved image
        im = cv2.imread(gfp)
        
        count = count + 1
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', im)
            im = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + im + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
