"""License.

Copyright 2018 PingguSoft <pinggusoft@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import keyboard

from utils import telloWithImageOutput
import os
from imageAnalysis.imageAnalysis import *
# import faceDetection
from utils.tello_utils import *

###############################################################################
# main
###############################################################################
print('Tello Controller                      ')
print('+------------------------------------+')
print('|  ESC(quit) 1(360) 2(bounce)        |')
print('+------------------------------------+')
print('|                                    |')
print('|      w                   up        |')
print('|  a       d          left    right  |')
print('|      s                  down       |')
print('|                                    |')
print('|         space(takeoff/land)        |')
print('|                                    |')
print('+------------------------------------+')

mDrone = telloWithImageOutput.Tello()
keyboard.hook(handleKey)
# clear folder first
fileList = os.listdir('./temp')
for fileName in fileList:
    os.remove("./temp/" + fileName)

# image parameters
width = 480
height = 360

n = 1
while True:
    img = cv2.imread('./temp/%08d.jpg' % n)

    if img is not None:

        resized_image = cv2.resize(img, (width, height))
        # img4, x, y=track_face(resized_image)
        x, y = None, None
        img5, x, y, w, h = recognize_face(resized_image)
        cv2.imshow("Hough", img5)
        cv2.waitKey(1)
        n += 1

        if y is not None:
            if y < 0:  # former up
                # mRCVal[IDX_THR] = RC_VAL_MAX
                mRCVal[IDX_THR] = RC_VAL_MID - y * (RC_VAL_MAX - RC_VAL_MID) / (height / 2)
                # print"going up"
            elif y > 0:  # former down
                # mRCVal[IDX_THR] = RC_VAL_MIN
                mRCVal[IDX_THR] = RC_VAL_MID - y * (RC_VAL_MAX - RC_VAL_MID) / (height / 2)
                # print"going down"
            else:
                mRCVal[IDX_THR] = RC_VAL_MID

            if x > 0:
                # mRCVal[IDX_YAW] = RC_VAL_MAX
                mRCVal[IDX_YAW] = RC_VAL_MID + x * (RC_VAL_MAX - RC_VAL_MID) / (width / 2)
                # print"going right "
            elif x < 0:
                # mRCVal[IDX_YAW] = RC_VAL_MIN
                mRCVal[IDX_YAW] = x * (RC_VAL_MAX - RC_VAL_MID) / (width / 2) + RC_VAL_MID
                # print"going left "
            else:
                mRCVal[IDX_YAW] = RC_VAL_MID

        else:
            mRCVal[IDX_THR] = RC_VAL_MID
            mRCVal[IDX_YAW] = RC_VAL_MID

        if w is not None:
            if w * h > 0.2 * resized_image.shape[0] * resized_image.shape[1]:
                mRCVal[IDX_PITCH] = RC_VAL_MIN + 550
                print("back")
            elif w * h < 0.1 * resized_image.shape[0] * resized_image.shape[1]:
                mRCVal[IDX_PITCH] = RC_VAL_MAX - 550
                print("forward")
            else:
                mRCVal[IDX_PITCH] = RC_VAL_MID
                print("stay")
        else:
            mRCVal[IDX_PITCH] = RC_VAL_MID
            print("stay")

    if isKeyPressed(KEY_MASK_ESC):
        break;

    # Toggle Keys
    if isKeyToggled(KEY_MASK_SPC):
        if isKeyPressed(KEY_MASK_SPC):
            mDrone.takeOff()
            print('take off')
        else:
            mDrone.land()
            print('land')
        clearToggle()

    # RC Keys
    # pitch / roll
    if isKeyPressed(KEY_MASK_RIGHT):
        mRCVal[IDX_ROLL] = RC_VAL_MAX
        print("rolling right ")
    elif isKeyPressed(KEY_MASK_LEFT):
        mRCVal[IDX_ROLL] = RC_VAL_MIN
        print("rolling left")
    else:
        mRCVal[IDX_ROLL] = RC_VAL_MID

    # if isKeyPressed(KEY_MASK_UP):
    #     mRCVal[IDX_PITCH] = RC_VAL_MAX
    #     print"rolling up"
    # elif isKeyPressed(KEY_MASK_DOWN):
    #     mRCVal[IDX_PITCH] = RC_VAL_MIN
    #     print"rolling down"
    # else:
    #     mRCVal[IDX_PITCH] = RC_VAL_MID

    mDrone.setStickData(0, int(mRCVal[IDX_ROLL]), int(mRCVal[IDX_PITCH]), int(mRCVal[IDX_THR]), int(mRCVal[IDX_YAW]))
    # print 'roll:{0:4d}, pitch:{1:4d}, thr:{2:4d}, yaw:{3:4d}'.format(mRCVal[IDX_ROLL], mRCVal[IDX_PITCH], mRCVal[IDX_THR], mRCVal[IDX_YAW])
mDrone.stop()
