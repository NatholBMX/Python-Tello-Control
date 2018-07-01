# Stream Video with OpenCV from an Android running IP Webcam (https://play.google.com/store/apps/details?id=com.pas.webcam)
# Code Adopted from http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera

import cv2
import numpy as np
import urllib.request, urllib.error, urllib.parse
# from imageAnalysis import imageAnalysis, handTracking
# from utils import detector_utils
from imageAnalysis import imageAnalysis
from imageAnalysis import objectTracker
import time

# host to our video stream
host = "192.168.1.7:8080"

hoststream = 'http://' + host + '/shot.jpg'

USE_WEBCAM = False


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
    # detection_graph, sess = detector_utils.load_inference_graph()
    # num_hands_detect = 1
    # score_thresh = 0.3
    # while True:
    #     img = get_img_from_stream()
    #     img6, x, y, _, _ = imageAnalysis.recognize_face(img)
    #     if x is None:
    #         boxes, scores = detector_utils.detect_objects(
    #             img, detection_graph, sess)
    #         detector_utils.draw_box_on_image(
    #             num_hands_detect, score_thresh, scores, boxes, img.shape[0], img.shape[1], img)
    #
    #     show_image(img6)

    # handTracking.init_cpm_session()
    # while True:
    #     img = get_img_from_stream()
    #     img2 = handTracking.trackHandCPM(img)
    #     show_image(img2)
    #     print(handTracking.tracker.loss_track)

    t_hand=0
    t_face=0
    current_diff=0
    find_hand=False
    while True:
        img = get_img_from_stream()
        if not find_hand:
            img2, x, _, _, _ = imageAnalysis.recognize_face(img)
            if x is not None:
                if t_face==0:
                    t_face=time.time()
                else:
                    current_diff=time.time()-t_face
            else:
                if t_hand==0:
                    t_hand=time.time()
                    print("T_hand: ", t_hand)
                    img2, x, y, w, h = imageAnalysis.detect_skin(img)
                else:
                    current_diff=time.time()-t_hand
                    img2, x, y, w, h = imageAnalysis.detect_skin(img)
                if current_diff>2:
                    find_hand=True
                    img2, x, y, w, h = imageAnalysis.detect_skin(img)
        else:
            print("in else")
            img2, x, y, w, h = imageAnalysis.detect_skin(img)
        show_image(img)

"""
TODO:
Timer for hand should start as before, but then the tracker should be initialized and object tracking should occur
If the timer finds no hand for more than 2 seconds, face should be tracked again-->reset tracker
"""
if __name__ == "__main__":
    main()
