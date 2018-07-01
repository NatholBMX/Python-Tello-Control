import cv2

tracker = cv2.TrackerGOTURN_create()
# Define an initial bounding box, format is x, y, w, h
bbox = None


def init_tracker(img, bounding_box):
    global tracker
    global bbox
    bbox = bounding_box
    ok = tracker.init(img, bounding_box)


def track_object(img):
    global tracker
    global bbox
    ok, bbox = tracker.update(img)

    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(img, p1, p2, (255, 0, 255), 2, 1)

    return img


def reset_tracker():
    global tracker
    global bbox
    cv2.TrackerGOTURN_create()
    bbox=None
