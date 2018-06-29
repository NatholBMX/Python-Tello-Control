# Stream Video with OpenCV from an Android running IP Webcam (https://play.google.com/store/apps/details?id=com.pas.webcam)
# Code Adopted from http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera

import cv2
import numpy as np
import urllib.request, urllib.error, urllib.parse
# from imageAnalysis import imageAnalysis, handTracking
# from utils import detector_utils
from imageAnalysis import handTracking

# host to our video stream
host = "192.168.1.35:8080"

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
    handTracking.init_cpm_session()
    while True:
        img = get_img_from_stream()
        img2 = handTracking.trackHandCPM(img)
        show_image(img2)
        print(handTracking.tracker.loss_track)


if __name__ == "__main__":
    main()
