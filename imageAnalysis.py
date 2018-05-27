import cv2
import numpy as np
from imutils import face_utils
import imutils
import dlib
import math

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./detector/det.dat')

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
    if lines is not None:
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


def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    # return a tuple of (x, y, w, h)
    return (x, y, w, h)


def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)

    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    # return the list of (x, y)-coordinates
    return coords

def track_face(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    centerX=None
    centerY=None
    w=None
    h=None
    for (i, rect) in enumerate(rects):
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # convert dlib's rectangle to a OpenCV-style bounding box
        # [i.e., (x, y, w, h)], then draw the face bounding box
        (x, y, w, h) = face_utils.rect_to_bb(rect)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        #calculate center of face rectangle
        pic_height = np.size(img, 0)
        pic_width = np.size(img, 1)
        centerX=x+w/2-pic_width/2
        centerY=y+h/2-pic_height/2

        #only keep first face found
        break



    return img, centerX, centerY