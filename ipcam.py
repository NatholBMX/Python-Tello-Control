# Stream Video with OpenCV from an Android running IP Webcam (https://play.google.com/store/apps/details?id=com.pas.webcam)
# Code Adopted from http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera

import cv2
import numpy as np
import urllib.request, urllib.error, urllib.parse
from imageAnalysis import imageAnalysis
from imageAnalysis import objectTracker
import time

# host to our video stream
host = "192.168.1.9:8080"

hoststream = 'http://' + host + '/shot.jpg'

USE_WEBCAM = False

# helper function for coordinate calculation
def computer_center_points(x, y, w, h):
    centerX = x + w / 2 - width / 2
    centerY = y + h / 2 - height / 2
    return centerX, centerY

def get_img_from_stream():
    if USE_WEBCAM:
        cam = cv2.VideoCapture(0)
        _, img = cam.read()
    else:
        # Use urllib to get the image and convert into a cv2 usable format
        imgResp = urllib.request.urlopen(hoststream)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
    return img


def show_image(img):
    cv2.imshow('IPWebcam', img)
    cv2.waitKey(1)


def main():

    t_hand = 0
    t_face = 0
    current_diff = 0
    hand_is_tracked=False

    while True:
        img = get_img_from_stream()
        if not hand_is_tracked:
            img2, x, _, _, _ = imageAnalysis.recognize_face(img)
            if x is not None:
                if t_face == 0:
                    t_face = time.time()
                else:
                    current_diff = time.time() - t_face
            else:
                if t_hand == 0:
                    t_hand = time.time()
                    img2, x, y, w, h = imageAnalysis.detect_skin(img)
                    if x is not None:
                        bbox = (x, y, w, h)
                        objectTracker.init_tracker(img, bbox)
                else:
                    current_diff = time.time() - t_hand
                    img2, x, y, w, h = imageAnalysis.detect_skin(img)
                    _, hand_is_tracked=objectTracker.track_object(img)
                if current_diff > 5:
                    img2, x, y, w, h = imageAnalysis.detect_skin(img)
                    _, hand_is_tracked=objectTracker.track_object(img)
        else:
            img2, x, y, w, h = imageAnalysis.detect_skin(img)
            _, hand_is_tracked = objectTracker.track_object(img)
            img2, x2, _, _, _ = imageAnalysis.recognize_face(img)
            if x2 is not None:
                if x is not None:
                    if t_face == 0:
                        t_face = time.time()
                    else:
                        current_diff = time.time() - t_face
                    if current_diff>5:
                        hand_is_tracked=False
                        t_face=0
                        t_hand=0
                        objectTracker.reset_tracker()
        show_image(img)

"""
ToDo:
Compute centerX and centerY of tracked objects in comparison to pic sizes for tracking
"""

if __name__ == "__main__":
    main()
