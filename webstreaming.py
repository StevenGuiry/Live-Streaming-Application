import argparse
import datetime
import imutils
import threading
import time
import csv
import smtplib
import ssl

from cv2 import cv2
from flask import Flask
from flask import Response
from flask import render_template
from imutils.video import VideoStream

from motiondetector import MotionDetector

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
    md = MotionDetector(accumWeight=0.35)
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
        # # Yield output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


def email_notifier():
    message = """Subject: Live Stream

        Hi {name}, we are live!!"""

    from_address = "s.guiry1@gmail.com"
    password = input("Type your password and press enter: ")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(from_address, password)
        with open("contacts_file.csv") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for name, email in reader:
                server.sendmail(
                    from_address,
                    email,
                    message.format(name=name),
                )


@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    # Command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # Starting thread that will perform motion detection
    t = threading.Thread(target=detect_motion, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()

    email_notifier()
    app.run(host="0.0.0.0", port=8080, debug=True,
            threaded=True, use_reloader=False)
# Release video stream
vs.stop()

# References:
# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
# https://realpython.com/python-send-email/
