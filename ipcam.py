# Stream Video with OpenCV from an Android running IP Webcam (https://play.google.com/store/apps/details?id=com.pas.webcam)
# Code Adopted from http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera

import cv2
import numpy as np
import urllib.request, urllib.error, urllib.parse
from imageAnalysis import imageAnalysis, handTracking
from utils import detector_utils

# host to our video stream
host = "192.168.1.3:8080"

hoststream = 'http://' + host + '/shot.jpg'

USE_WEBCAM = True


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


def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


def draw_hough_lines(edge_image, original_img):
    minLineLength = 30
    maxLineGap = 10
    lines = cv2.HoughLinesP(edge_image, 1, np.pi / 180, 15, minLineLength, maxLineGap)
    for x in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[x]:
            cv2.line(original_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return original_img


def draw_countours(original_img):
    imgray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 130, 255, 0)
    _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(original_img, contours, -1, (0, 0, 255), 3)
    return original_img


def find_red(original_img):
    # create lower and upper bounds for red
    red_lower = np.array([17, 15, 100], dtype="uint8")
    red_upper = np.array([50, 56, 200], dtype="uint8")

    # perform the filtering. mask is another word for filter
    mask = cv2.inRange(original_img, red_lower, red_upper)
    output = cv2.bitwise_and(original_img, original_img, mask=mask)
    # convert the image to grayscale, then calculate the center of the red (only remaining color)
    # output_gray = rgb2gray(output)
    return output


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

    while True:
        img = get_img_from_stream()
        handTracking.trackHandCPM(img)



if __name__ == "__main__":
    main()
