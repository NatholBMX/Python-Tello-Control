import cv2
import numpy as np
import face_recognition


def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


def draw_hough_lines(edge_image, original_img):
    minLineLength = 30
    maxLineGap = 10
    lines = cv2.HoughLinesP(edge_image, 1, np.pi / 180, 15, minLineLength, maxLineGap)
    if lines is not None:
        for x in range(0, len(lines)):
            for x1, y1, x2, y2 in lines[x]:
                cv2.line(original_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return original_img


def draw_countours(original_img):
    imgray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 130, 255, 0)
    _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(original_img, contours, -1, (0, 0, 255), 3)
    return original_img


def find_red(original_img):
    # create lower and upper bounds for red
    red_lower = np.array([17, 15, 100], dtype="uint8")
    red_upper = np.array([50, 56, 200], dtype="uint8")

    # perform the filtering. mask is another word for filter
    mask = cv2.inRange(original_img, red_lower, red_upper)
    output = cv2.bitwise_and(original_img, original_img, mask=mask)
    # convert the image to grayscale, then calculate the center of the red (only remaining color)
    # output_gray = rgb2gray(output)
    return output


def track_hand(img):
    w=None
    h=None
    # Blur the image
    blur = cv2.blur(img, (3, 3))

    # Convert to HSV color space
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Create a binary image with where white will be skin colors and rest is black
    mask2 = cv2.inRange(hsv, np.array([2, 50, 50]), np.array([15, 255, 255]))

    # Kernel matrices for morphological transformation
    kernel_square = np.ones((11, 11), np.uint8)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # Perform morphological transformations to filter out the background noise
    # Dilation increase skin color area
    # Erosion increase skin color area
    dilation = cv2.dilate(mask2, kernel_ellipse, iterations=1)
    erosion = cv2.erode(dilation, kernel_square, iterations=1)
    dilation2 = cv2.dilate(erosion, kernel_ellipse, iterations=1)
    filtered = cv2.medianBlur(dilation2, 5)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
    dilation2 = cv2.dilate(filtered, kernel_ellipse, iterations=1)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilation3 = cv2.dilate(filtered, kernel_ellipse, iterations=1)
    median = cv2.medianBlur(dilation2, 5)
    ret, thresh = cv2.threshold(median, 127, 255, 0)

    # Find contours of the filtered frame
    img2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:

        # Find Max contour area (Assume that hand is in the frame)
        max_area = 100
        ci = 0
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if (area > max_area):
                max_area = area
                ci = i

            # Largest area contour
        cnts = contours[ci]

        # Find convex hull
        hull = cv2.convexHull(cnts)

        # Find convex defects
        hull2 = cv2.convexHull(cnts, returnPoints=False)
        defects = cv2.convexityDefects(cnts, hull2)

        # Get defect points and draw them in the original image
        FarDefect = []
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(cnts[s][0])
            end = tuple(cnts[e][0])
            far = tuple(cnts[f][0])
            FarDefect.append(far)
            #cv2.line(img, start, end, [0, 255, 0], 1)
            # cv2.circle(img, far, 10, [100, 255, 255], 3)

        # Find moments of the largest contour
        moments = cv2.moments(cnts)

        # Central mass of first order moments
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])  # cx = M10/M00
            cy = int(moments['m01'] / moments['m00'])  # cy = M01/M00
        centerMass = (cx, cy)

        # Draw center mass
        #cv2.circle(img, centerMass, 7, [100, 0, 255], 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.putText(img, 'Center', tuple(centerMass), font, 2, (255, 255, 255), 2)

        # Distance from each finger defect(finger webbing) to the center mass
        distanceBetweenDefectsToCenter = []
        for i in range(0, len(FarDefect)):
            x = np.array(FarDefect[i])
            centerMass = np.array(centerMass)
            distance = np.sqrt(np.power(x[0] - centerMass[0], 2) + np.power(x[1] - centerMass[1], 2))
            distanceBetweenDefectsToCenter.append(distance)

        # Get an average of three shortest distances from finger webbing to center mass
        sortedDefectsDistances = sorted(distanceBetweenDefectsToCenter)
        AverageDefectDistance = np.mean(sortedDefectsDistances[0:2])

        # Get fingertip points from contour hull
        # If points are in proximity of 80 pixels, consider as a single point in the group
        finger = []
        for i in range(0, len(hull) - 1):
            if (np.absolute(hull[i][0][0] - hull[i + 1][0][0]) > 80) or (
                    np.absolute(hull[i][0][1] - hull[i + 1][0][1]) > 80):
                if hull[i][0][1] < 500:
                    finger.append(hull[i][0])

        # The fingertip points are 5 hull points with largest y coordinates
        finger = sorted(finger, key=lambda x: x[1])
        fingers = finger[0:5]

        # Calculate distance of each finger tip to the center mass
        fingerDistance = []
        for i in range(0, len(fingers)):
            distance = np.sqrt(np.power(fingers[i][0] - centerMass[0], 2) + np.power(fingers[i][1] - centerMass[0], 2))
            fingerDistance.append(distance)

        # Finger is pointed/raised if the distance of between fingertip to the center mass is larger
        # than the distance of average finger webbing to center mass by 130 pixels
        result = 0
        for i in range(0, len(fingers)):
            if fingerDistance[i] > AverageDefectDistance + 130:
                result = result + 1
        if result <= 2:
            return img, w, h
        else:
            # Print number of pointed fingers
            cv2.putText(img, str(result), (100, 100), font, 2, (255, 255, 255), 2)

            # Print bounding rectangle
            # rect = cv2.minAreaRect(cnts)
            # box = cv2.boxPoints(rect)
            # w, h=box[3]
            # print w
            # print h
            # box = np.int0(box)
            # img = cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
            x, y, w, h = cv2.boundingRect(cnts)
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.drawContours(img, [hull], -1, (255, 255, 255), 2)
            return img, w, h
    return img, w, h


def recognize_face(img):
    face_locations = face_recognition.face_locations(img, number_of_times_to_upsample=0, model="cnn")
    centerX = None
    centerY = None
    face_width=None
    face_height=None
    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)

        pic_height = np.size(img, 0)
        pic_width = np.size(img, 1)
        face_width = right - left
        face_height = bottom - top

        centerX = left + face_width / 2 - pic_width / 2
        centerY = top + face_height / 2 - pic_height / 2
        break

    return img, centerX, centerY, face_width, face_height
