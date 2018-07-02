import cv2

DEBUGGING = True

#tracker = cv2.TrackerGOTURN_create()
# tracker = cv2.TrackerMedianFlow_create()
# tracker = cv2.TrackerTLD_create()
tracker = cv2.TrackerBoosting_create()
# tracker = cv2.TrackerMIL_create()
# tracker = cv2.TrackerKCF_create()
# Define an initial bounding box, format is x, y, w, h
bbox = None


def init_tracker(img, bounding_box):
    global tracker
    global bbox
    bbox = bounding_box
    tracked = tracker.init(img, bounding_box)


def track_object(img):
    global tracker
    global bbox
    tracked, bbox = tracker.update(img)

    if tracked:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        if DEBUGGING:
            cv2.rectangle(img, p1, p2, (255, 0, 255), 2, 1)
    else:
        bbox = None

    return img, tracked


def reset_tracker():
    global tracker
    global bbox
    tracker = cv2.TrackerBoosting_create()
    bbox = None
