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

import time
import keyboard
import telloWithImageOutput
import cv2
import os
from imageAnalysis import *
#import faceDetection

###############################################################################
# constants
###############################################################################
KEY_MASK_UP = 0x0001
KEY_MASK_DOWN = 0x0002
KEY_MASK_LEFT = 0x0004
KEY_MASK_RIGHT = 0x0008
KEY_MASK_W = 0x0010
KEY_MASK_S = 0x0020
KEY_MASK_A = 0x0040
KEY_MASK_D = 0x0080
KEY_MASK_SPC = 0x0100
KEY_MASK_1 = 0x0200
KEY_MASK_2 = 0x0400
KEY_MASK_ESC = 0x8000

RC_VAL_MIN = 364
RC_VAL_MID = 1024
RC_VAL_MAX = 1684

IDX_ROLL = 0
IDX_PITCH = 1
IDX_THR = 2
IDX_YAW = 3

###############################################################################
# global variables
###############################################################################
mKeyFlags = 0
mOldKeyFlags = 0
mRCVal = [1024, 1024, 1024, 1024]


###############################################################################
# functions
###############################################################################
def isKeyPressed(mask):
    if mKeyFlags & mask == mask:
        return True
    return False


def isKeyToggled(mask):
    if (mKeyFlags & mask) != (mOldKeyFlags & mask):
        return True
    return False


def setFlag(e, mask):
    global mKeyFlags
    if e.event_type == 'down':
        mKeyFlags = mKeyFlags | mask
    else:
        mKeyFlags = mKeyFlags & ~mask


def toggleFlag(e, mask):
    global mKeyFlags
    if e.event_type == 'up':
        if mKeyFlags & mask == mask:
            mKeyFlags = mKeyFlags & ~mask
        else:
            mKeyFlags = mKeyFlags | mask


def clearToggle():
    global mOldKeyFlags
    mOldKeyFlags = mKeyFlags


tblKeyFunctions = {
    #    key      toggle   mask
    'up': (False, KEY_MASK_UP),
    'down': (False, KEY_MASK_DOWN),
    'left': (False, KEY_MASK_LEFT),
    'right': (False, KEY_MASK_RIGHT),
    'w': (False, KEY_MASK_W),
    's': (False, KEY_MASK_S),
    'a': (False, KEY_MASK_A),
    'd': (False, KEY_MASK_D),
    'esc': (False, KEY_MASK_ESC),
    'space': (True, KEY_MASK_SPC),
    '1': (True, KEY_MASK_1),
    '2': (True, KEY_MASK_2),
}


def handleKey(e):
    global mKeyFlags
    if e.name in tblKeyFunctions:
        if tblKeyFunctions[e.name][0] == False:
            setFlag(e, tblKeyFunctions[e.name][1])
        else:
            toggleFlag(e, tblKeyFunctions[e.name][1])

###############################################################################
# main
###############################################################################
print 'Tello Controller                      '
print '+------------------------------------+'
print '|  ESC(quit) 1(360) 2(bounce)        |'
print '+------------------------------------+'
print '|                                    |'
print '|      w                   up        |'
print '|  a       d          left    right  |'
print '|      s                  down       |'
print '|                                    |'
print '|         space(takeoff/land)        |'
print '|                                    |'
print '+------------------------------------+'

mDrone = telloWithImageOutput.Tello()
keyboard.hook(handleKey)
# clear folder first
fileList = os.listdir('./temp')
for fileName in fileList:
    os.remove("./temp/"+fileName)

# image parameters
width=160
height=120

n=1
while True:
    img = cv2.imread('./temp/%08d.jpg' % n)

    if img is not None:

        resized_image = cv2.resize(img, (width, height))
        img4, x, y=track_face(resized_image)

        #if x is not None:
            #print "x, y " +str(x) +" "+str(y)
        cv2.imshow("Hough", img4)
        cv2.waitKey(1)
        n += 1

        if y is not None:
            if y < 0:  # former up
                #mRCVal[IDX_THR] = RC_VAL_MAX
                mRCVal[IDX_THR] = RC_VAL_MID-y*(RC_VAL_MAX-RC_VAL_MID)/(height/2)
                #print"going up"
            elif y > 0:  # former down
                #mRCVal[IDX_THR] = RC_VAL_MIN
                mRCVal[IDX_THR] = RC_VAL_MID-y*(RC_VAL_MAX-RC_VAL_MID)/(height/2)
                #print"going down"
            else:
                mRCVal[IDX_THR] = RC_VAL_MID

            if x>0:
                #mRCVal[IDX_YAW] = RC_VAL_MAX
                mRCVal[IDX_YAW] = RC_VAL_MID+x*(RC_VAL_MAX-RC_VAL_MID)/(width/2)
                #print"going right "
            elif x<0:
                #mRCVal[IDX_YAW] = RC_VAL_MIN
                mRCVal[IDX_YAW] = x*(RC_VAL_MAX-RC_VAL_MID)/(width/2)+RC_VAL_MID
                #print"going left "
            else:
                mRCVal[IDX_YAW] = RC_VAL_MID

        else:
            mRCVal[IDX_THR] = RC_VAL_MID
            mRCVal[IDX_YAW] = RC_VAL_MID




    if isKeyPressed(KEY_MASK_ESC):
        break;

    # Toggle Keys
    if isKeyToggled(KEY_MASK_SPC):
        if isKeyPressed(KEY_MASK_SPC):
            mDrone.takeOff()
            print 'take off'
        else:
            mDrone.land()
            print 'land'
        clearToggle()


    # RC Keys
    # pitch / roll

    if isKeyPressed(KEY_MASK_RIGHT):
        mRCVal[IDX_ROLL] = RC_VAL_MAX
        print"rolling right "
    elif isKeyPressed(KEY_MASK_LEFT):
        mRCVal[IDX_ROLL] = RC_VAL_MIN
        print "rolling left"
    else:
        mRCVal[IDX_ROLL] = RC_VAL_MID

    if isKeyPressed(KEY_MASK_UP):
        mRCVal[IDX_PITCH] = RC_VAL_MAX
        print"rolling up"
    elif isKeyPressed(KEY_MASK_DOWN):
        mRCVal[IDX_PITCH] = RC_VAL_MIN
        print"rolling down"
    else:
        mRCVal[IDX_PITCH] = RC_VAL_MID

    mDrone.setStickData(0, mRCVal[IDX_ROLL], mRCVal[IDX_PITCH], mRCVal[IDX_THR], mRCVal[IDX_YAW])
    #print 'roll:{0:4d}, pitch:{1:4d}, thr:{2:4d}, yaw:{3:4d}'.format(mRCVal[IDX_ROLL], mRCVal[IDX_PITCH], mRCVal[IDX_THR], mRCVal[IDX_YAW])
mDrone.stop()
