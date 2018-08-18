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
width = 720
height = 540

# flag for saving video
SAVE_VIDEO = False

# list of modes supported
mode_list = ["faceTracking", "handTracking", "gestureControl"]

face_counter = 0


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
    global face_counter

    throttleValue = 0
    yawValue = 0
    pitchValue = 0

    # implement faceTracking
    if mode == mode_list[0]:
        _, centerX, centerY, faceWidth, faceHeight = imageAnalysis.recognize_face(image)

        if centerX is not None:
            face_counter = 0

            throttleValue = -centerY / (height / 2)
            yawValue = centerX / (width / 2)
            pitchValue = 0
            if faceWidth * faceHeight > 0.1 * width * height:  # 0.2
                pitchValue = -0.2
            elif faceWidth * faceHeight < 0.01 * width * height:  # 0.05
                pitchValue = 0.2
        else:
            throttleValue = 0
            yawValue = 0
            pitchValue = 0
            face_counter += 1

    # implement handTracking
    elif mode == mode_list[1]:
        face_counter = 0
        img2, x, y, w, h = handTracking.trackHandCPM(image)

        if not handTracking.tracker.loss_track:
            centerX, centerY = computer_center_points(x, y, w, h, image)
            throttleValue = -centerY / (height / 2)
            yawValue = centerX / (width / 2)
            if w * h >= 0.01 * width * height:
                pitchValue = -0.2
            elif w * h < 0.008 * width * height:
                pitchValue = 0.2
        else:
            throttleValue = 0
            yawValue = 0
            pitchValue = 0

    return throttleValue, yawValue, pitchValue


def set_gesture_counter(gesture, gesture_counter):
    gesture_index = handTracking.gesture_list.index(gesture)

    temp_counter = gesture_counter[gesture_index] + 1
    gesture_counter = [0] * len(handTracking.gesture_list)
    gesture_counter[gesture_index] = temp_counter

    return gesture_counter


def main():
    handTracking.init_cpm_session()
    drone = tellopy.Tello()

    mode = mode_list[1]
    trackFace = False
    global face_counter

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

        gesture_counter = [0] * len(handTracking.gesture_list)
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

                start_time = time.time()

                img = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                if SAVE_VIDEO:
                    out.write(img)

                resized_image = cv2.resize(img, (width, height))

                if not imageAnalysis.found_face:
                    gesture = handTracking.get_gesture(resized_image)
                # print("Gesture: "+str(gesture)+" Counter: "+str(gesture_counter))

                if gesture == "pitch":
                    gesture_counter = set_gesture_counter("pitch", gesture_counter)
                    if gesture_counter[0] >= 10:
                        drone.land()
                elif gesture == "fist":
                    gesture_counter = set_gesture_counter("fist", gesture_counter)
                    if gesture_counter[1] >= 10:
                        drone.takeoff()
                elif gesture == "victory":
                    #print(gesture_counter)
                    gesture_counter = set_gesture_counter("victory", gesture_counter)
                    if gesture_counter[2] >= 25:
                        trackFace = not trackFace
                        gesture_counter = set_gesture_counter("pitch", gesture_counter)

                if trackFace:
                    if face_counter >= 50:
                        trackFace = False
                        mode = mode_list[1]
                    else:
                        mode = mode_list[0]
                else:
                    mode = mode_list[1]

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
