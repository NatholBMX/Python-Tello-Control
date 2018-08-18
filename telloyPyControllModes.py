"""
Module supporting different modes for flying the Tello drone
"""

import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time
from imageAnalysis import handTracking, imageAnalysis
import pygame

# image resize parameters
width = 480
height = 360

# flag for saving video
SAVE_VIDEO = True

# list of modes supported
mode_list = ["faceTracking", "handTracking", "gestureControl"]


def show_image(img):
    cv2.imshow('IPWebcam', img)
    cv2.waitKey(1)


def computer_center_points(x, y, w, h, img):
    height = numpy.size(img, 0)
    width = numpy.size(img, 1)
    centerX = x + w / 2 - width / 2
    centerY = y + h / 2 - height / 2
    return centerX, centerY


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def control_drone_by_mode(image, mode=None):
    if mode == None:
        throttleValue = 0
        yawValue = 0
        pitchValue = 0

    # implement faceTracking
    elif mode == mode_list[0]:
        _, centerX, centerY, faceWidth, faceHeight = imageAnalysis.recognize_face(image)

        if centerX is not None:
            throttleValue = -centerY / (height / 2)
            yawValue = centerX / (width / 2)
            pitchValue = 0
            if faceWidth * faceHeight > 0.2 * width * height:
                pitchValue = -0.2
            elif faceWidth * faceHeight < 0.05 * width * height:
                pitchValue = 0.2
        else:
            throttleValue = 0
            yawValue = 0
            pitchValue = 0

    # implement handTracking
    elif mode == mode_list[1]:
        img2, x, y, w, h = handTracking.trackHandCPM(image)

        if not handTracking.tracker.loss_track:
            centerX, centerY = computer_center_points(x, y, w, h, image)
            throttleValue = -centerY / (height / 2)
            yawValue = centerX / (width / 2)
            if w * h >= 0.015 * width * height:
                pitchValue = -0.2
            elif w * h < 0.008 * width * height:
                pitchValue = 0.2
        else:
            throttleValue = 0
            yawValue = 0
            pitchValue = 0

    return throttleValue, yawValue, pitchValue

def set_gesture_counter(gesture, gesture_counter):
    gesture_index=handTracking.gesture_list.index(gesture)

    temp_counter=gesture_counter[gesture_index]+1
    gesture_counter = [0] * len(handTracking.gesture_list)
    gesture_counter[gesture_index]=temp_counter

    return gesture_counter


def main():
    handTracking.init_cpm_session()
    drone = tellopy.Tello()

    mode = None

    try:
        pygame.init()
        pygame.display.set_mode((1, 1))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output.avi', fourcc, 15.0, (960, 720))
        drone.connect()
        drone.wait_for_connection(60.0)

        container = av.open(drone.get_video_stream())
        # skip first 300 frames
        frame_skip = 300

        gesture_counter=[0]*len(handTracking.gesture_list)
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LCTRL:
                            drone.takeoff()
                        if event.key == pygame.K_w:
                            drone.land()
                        if event.key == pygame.K_0:
                            mode = None
                        if event.key == pygame.K_1:
                            mode = mode_list[0]
                        if event.key == pygame.K_2:
                            mode = mode_list[1]

                start_time = time.time()

                img = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                if SAVE_VIDEO:
                    out.write(img)

                resized_image = cv2.resize(img, (width, height))

                img2, x, y, w, h = handTracking.trackHandCPM(resized_image)
                gesture = handTracking.get_gesture(resized_image)

                if gesture == "pitch":
                    gesture_counter=set_gesture_counter("pitch", gesture_counter)
                    print(gesture_counter)
                    if gesture_counter[0] >= 10:
                        drone.land()

                elif gesture == "fist":
                    pitchCounter = 0
                    fistCounter += 1
                    victoryCounter = 0

                    if gesture_counter[1] >= 5:
                        drone.takeoff()
                elif gesture == "victory":
                    pitchCounter = 0
                    fistCounter = 0
                    victoryCounter += 1

                    if gesture_counter[2] >= 5:
                        drone.up(70)
                        time.sleep(0.5)
                        drone.down(70)
                        time.sleep(0.5)

                throttleValue, yawValue, pitchValue = control_drone_by_mode(resized_image, mode)

                drone.set_throttle(throttleValue)
                drone.set_yaw(yawValue)
                drone.set_pitch(pitchValue)

                show_image(resized_image)
                frame_skip = int((time.time() - start_time) / frame.time_base)



    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
