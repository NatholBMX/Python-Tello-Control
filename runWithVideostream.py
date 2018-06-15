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
from utils import telloWithVideostream
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

mDrone = telloWithVideostream.Tello()
keyboard.hook(handleKey)

while True:
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

    if isKeyToggled(KEY_MASK_1):
        if isKeyPressed(KEY_MASK_1):
            mDrone.setSmartVideoShot(telloWithVideostream.Tello.TELLO_SMART_VIDEO_360, True)
            print('SmartVideo 360 start')
        else:
            mDrone.setSmartVideoShot(telloWithVideostream.Tello.TELLO_SMART_VIDEO_360, False)
            print('SmartVideo 360 stop')
        clearToggle()

    if isKeyToggled(KEY_MASK_2):
        if isKeyPressed(KEY_MASK_2):
            mDrone.bounce(True)
            print('Bounce start')
        else:
            mDrone.bounce(False)
            print('Bounce stop')
        clearToggle()

    # RC Keys
    # pitch / roll
    if isKeyPressed(KEY_MASK_RIGHT):
        mRCVal[IDX_ROLL] = RC_VAL_MAX
    elif isKeyPressed(KEY_MASK_LEFT):
        mRCVal[IDX_ROLL] = RC_VAL_MIN
    else:
        mRCVal[IDX_ROLL] = RC_VAL_MID

    if isKeyPressed(KEY_MASK_UP):
        mRCVal[IDX_PITCH] = RC_VAL_MAX
    elif isKeyPressed(KEY_MASK_DOWN):
        mRCVal[IDX_PITCH] = RC_VAL_MIN
    else:
        mRCVal[IDX_PITCH] = RC_VAL_MID

    # thr / yaw
    if isKeyPressed(KEY_MASK_W):
        mRCVal[IDX_THR] = RC_VAL_MAX
    elif isKeyPressed(KEY_MASK_S):
        mRCVal[IDX_THR] = RC_VAL_MIN
    else:
        mRCVal[IDX_THR] = RC_VAL_MID

    if isKeyPressed(KEY_MASK_D):
        mRCVal[IDX_YAW] = RC_VAL_MAX
    elif isKeyPressed(KEY_MASK_A):
        mRCVal[IDX_YAW] = RC_VAL_MIN
    else:
        mRCVal[IDX_YAW] = RC_VAL_MID

    mDrone.setStickData(0, mRCVal[IDX_ROLL], mRCVal[IDX_PITCH], mRCVal[IDX_THR], mRCVal[IDX_YAW])
    # print 'roll:{0:4d}, pitch:{1:4d}, thr:{2:4d}, yaw:{3:4d}'.format(mRCVal[IDX_ROLL], mRCVal[IDX_PITCH], mRCVal[IDX_THR], mRCVal[IDX_YAW])

mDrone.stop()
