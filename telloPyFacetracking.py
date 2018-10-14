import sys
import traceback
import tellopy
import av
import numpy
import time
from imageAnalysis import imageAnalysis
import pygame
from utils.params import *


def show_image(img):
    cv2.imshow('IPWebcam', img)
    cv2.waitKey(1)


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def main():
    drone = tellopy.Tello()

    try:
        pygame.init()
        pygame.display.set_mode((1, 1))
        drone.connect()
        drone.wait_for_connection(60.0)

        container = av.open(drone.get_video_stream())

        # skip first 300 frames
        frame_skip = 300
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
                img = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                resized_image = cv2.resize(img, (IMAGE_WIDTH, IMAGE_HEIGHT))

                _, centerX, centerY, faceWidth, faceHeight = imageAnalysis.recognize_face(resized_image)

                if centerX is not None:
                    throttleValue = -centerY / (IMAGE_HEIGHT / 2)
                    yawValue = centerX / (IMAGE_WIDTH / 2)
                    pitchValue = 0
                    if faceWidth * faceHeight > 0.2 * IMAGE_WIDTH * IMAGE_HEIGHT:
                        pitchValue = -0.2
                    elif faceWidth * faceHeight < 0.05 * IMAGE_WIDTH * IMAGE_HEIGHT:
                        pitchValue = 0.2
                    drone.set_throttle(throttleValue)
                    drone.set_yaw(yawValue)
                    drone.set_pitch(pitchValue)
                else:
                    drone.set_throttle(0)
                    drone.set_yaw(0)
                    drone.set_pitch(0)

                show_image(resized_image)
                start_time = time.time()

                frame_skip = int((time.time() - start_time) / frame.time_base)



    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        # safely land drone
        drone.land()
        time.sleep(5)
        drone.quit()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
