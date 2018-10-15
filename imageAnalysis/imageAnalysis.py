import cv2
import numpy as np
import face_recognition
from utils.params import *

DEBUGGING = True

FOUND_FACE = False

# personal face encoding
PERSONAL_ENCODING = []


def learn_personal_face():
    global PERSONAL_ENCODING
    face_image = face_recognition.load_image_file(PERSONAL_FACE_LOCATION)
    encoding = face_recognition.face_encodings(face_image)[0]
    PERSONAL_ENCODING.append(encoding)


def recognize_face(img):
    face_locations = face_recognition.face_locations(img, number_of_times_to_upsample=0, model="cnn")
    face_encodings = face_recognition.face_encodings(img, face_locations)
    centerX = None
    centerY = None
    face_width = None
    face_height = None

    global FOUND_FACE
    if len(face_locations) > 0:
        FOUND_FACE = True
    else:
        FOUND_FACE = False
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

        if PERSONAL_FACE_RECOGNITION:
            matches = face_recognition.compare_faces(PERSONAL_ENCODING, face_encoding)
        else:
            matches=[True,]
        # Print the location of each face in this image
        # top, right, bottom, left = face_location
        if DEBUGGING:
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)

        if True in matches:
            pic_height = np.size(img, 0)
            pic_width = np.size(img, 1)
            face_width = right - left
            face_height = bottom - top

            centerX = left + face_width / 2 - pic_width / 2
            centerY = top + face_height / 2 - pic_height / 2
            break

    return img, centerX, centerY, face_width, face_height


def detect_skin(img):
    # return values
    x = None
    y = None
    hand_width = None
    hand_height = None

    # Constants for finding range of skin color in YCrCb
    min_YCrCb = np.array([80, 150, 77], np.uint8)
    max_YCrCb = np.array([255, 173, 127], np.uint8)

    # Convert image to YCrCb
    imageYCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)

    # Find region with skin tone in YCrCb image
    skinRegion = cv2.inRange(imageYCrCb, min_YCrCb, max_YCrCb)

    # Do contour detection on skin region
    _, contours, hierarchy, = cv2.findContours(skinRegion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # Find the largest contour and draw it
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)

        # contour approximation
        epsilon = 0.01 * cv2.arcLength(contours[max_index], True)
        approx = cv2.approxPolyDP(contours[max_index], epsilon, True)

        if len(approx) <= 20:
            img, x, y, hand_width, hand_height = draw_bounding_box_from_contour(img, contours[max_index])

        x, y, hand_width, hand_height = cv2.boundingRect(contours[max_index])
    return img, x, y, hand_width, hand_height


def draw_bounding_box_from_contour(img, contour):
    x, y, w, h = cv2.boundingRect(contour)
    if DEBUGGING:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
    pic_height = np.size(img, 0)
    pic_width = np.size(img, 1)
    centerX = x + w / 2 - pic_width / 2
    centerY = y + h / 2 - pic_height / 2
    return img, centerX, centerY, w, h
