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
global mKeyFlags
mKeyFlags = 0
global mOldKeyFlags
mOldKeyFlags = 0
mRCVal = [1024, 1024, 1024, 1024]

###############################################################################
# key mapping
###############################################################################

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


###############################################################################
# key handling methods
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


def handleKey(e):
    if e.name in tblKeyFunctions:
        if tblKeyFunctions[e.name][0] == False:
            setFlag(e, tblKeyFunctions[e.name][1])
        else:
            toggleFlag(e, tblKeyFunctions[e.name][1])
