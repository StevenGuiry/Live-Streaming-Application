import numpy as np
import imutils
from cv2 import cv2


class MotionDetector:
    def __init__(self, accumWeight=0.5):
        self.accumWeight = accumWeight

        self.bg = None

    def update(self, image):
        # Initialise background model if None.
        if self.bg is None:
            self.bg = image.copy().astype("float")
            return
        # Update background model by accumulating weighted average
        cv2.accumulateWeighted(image, self.bg, self.accumWeight)

    def detect(self, image, tVal=25):
        # Compute the absolute difference between the bg model and the
        # image passed in
        delta = cv2.absdiff(self.bg.astype("uint8"), image)
        thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]

        # Clean up image by performing series of erosion/dilutions
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find any contours in the image and initialize the min and max
        # bounding box regions for motion detected
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        (minX, minY) = (np.inf, np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)

        # Populate above variables if motion exists in the frame

        # If no contours are found
        if len(cnts) == 0:
            return None

        # Otherwise, loop over contours
        for c in cnts:
            # Get the bounding box of the contour and use it to update
            # the min and max regions
            (x, y, w, h) = cv2.boundingRect(c)
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))

        return (thresh, (minX, minY, maxX, maxY))
