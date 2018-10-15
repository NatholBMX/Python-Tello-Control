"""
Module for keeping all relevant parameters
"""

import cv2.cv2 as cv2

# image resizing parameters
IMAGE_WIDTH = 480
IMAGE_HEIGHT = 360

# Video parameters
SAVE_VIDEO = True
VIDEO_FILENAME = "output.avi"
VIDEO_CODEC = cv2.VideoWriter_fourcc(*'mp4v')

# Personalize face recognition
PERSONAL_FACE_RECOGNITION = True
PERSONAL_FACE_LOCATION = "personal_face/01.png"
