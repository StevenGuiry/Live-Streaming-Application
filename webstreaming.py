from motiondetector import MotionDetector
from cv2 import cv2
from imutils.video import VideoStream
from flask import Flask
from flask import Response
from flask import render_template
import threading, argparse, datetime, imutils, time

outputFrame = None
lock = threading.Lock()

# Initialize flask object
app = Flask(__name__)

vs = VideoStream(src=0).start()
time.sleep(2.0)


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


def detect_motion(frameCount):
    # Get global references
    global vs, outputFrame, lock

    # Initialize motion detector
    md = MotionDetector(accumWeight=0.1)
    total = 0

    while True:
        # Reading next frame from the video stream, resize and convert to greyscale
        # and blur it
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # Get timestamp and draw it on frame
        timestamp = datetime.datetime.now()
        cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                    cv2.FONT_ITALIC, 0.35, (0, 0, 255), 1)
        if total > frameCount:
            motion = md.detect(gray)

            # Check to see if motion was detected
            if motion is not None:
                # Draw the box around the motion area
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                              (0, 0, 255), 2)

        md.update(gray)
        total += 1

        # Acquire lock, set output frame then release lock
        with lock:
            outputFrame = frame.copy()


def generate():
    # Global references
    global outputFrame, lock

    # Loop over frames from the output stream
    while True:
        with lock:
            # Check if output frame is available
            if outputFrame is None:
                continue
            # Encode frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            if not flag:
                continue
        # Yield output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    # Command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # Starting thread that will perform motion detection
    t = threading.Thread(target=detect_motion, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()

    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)
# Release video stream
vs.stop()

# Reference: https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
