#!/usr/bin/env python3
import cv2
import numpy as np
import math

# cv2 attributes
cap = cv2.VideoCapture("fish.mp4")
# cap = cv2.VideoCapture(1)

# Globals
font = cv2.FONT_HERSHEY_SIMPLEX
# Use this
padding = 200 
# Or
paddingWidth = 200 
paddingHeight = 200

def angleBetween(p1, p2):
    """Calculates the angle at which the center of the fish is offset from the origin 

    Args:
        p1 (tuple): coordinates to point one
        p2 (tuple): coordinates to point two

    Returns:
        float: our angle in degrees
    """
    # Our angle in radians
    rads = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    # Returns precise but in reference is rounded
    return math.degrees(rads)

def determineDir(angle):
    """Function to determine which of the eight cardinal directions our angle corelates to

    Args:
        angle (float): The angle in degress, not radians

    Raises:
        Exception: Any - to catch errors that were occuring

    Returns:
        string: A 1-2 character long repersentation of our direction
    """
    # N = -112.5 - -67.5
    # NE = -67.5 - -22.5
    # E = -22.5 - 22.5
    # SE = 22.5 - 67.5
    # S = 67.5 - 112.5
    # SW = 112.5 - 157.5
    # W = 157.5 - -157.5
    # NW = -157.5 - -112.5
    try:
        if -112.5 <= angle <= -67.5:
            return 'N'
        elif -67.5 <= angle <= -22.5:
            return 'NE'
        elif -22.5 <= angle <= 22.5:
            return 'E'
        elif 22.5 <= angle <= 67.5:
            return 'SE'
        elif 67.5 <= angle <= 112.5:
            return 'S'
        elif 112.5 <= angle <= 157.5:
            return 'SW'
        elif 157.5 <= angle <= 180 or -157.5 <= angle <= -112.5:
            return 'W'
        elif 157.5 <= angle <= -112.5:
            return 'NW'
        else:
            return "COCK"
    except:
        raise Exception("Error in determineDir()")

def outOfEdge(x, y, w, h, leftEdge, rightEdge, topEdge, bottomEdge):
    """A function to determine if the center of our fish is out of the bounds of the center padding box

    Args:
        x (Any(int, float)): The x coordinate of our fish
        y (Ant(int, float)): The y coordinate of our fish
        w (Any(int, float)): The width of our fish's bounding box
        h (Any(int, float)): The heigh of our fish's bounding box
        leftEdge (Any(int, float)): The x coordinate of the left edge of our center padding box
        rightEdge (Any(int, float)): The x coordinate of the right edge of our center padding box
        topEdge (Any(int, float)): The y coordinate of the top edge of our center padding box
        bottomEdge (Any(int, float)): The y coordinate of the bottom edge of our center padding box

    Returns:
        bool: True if the fish is out of bounds, False if not
    """
    centerX = (x + (x+w)) / 2
    centerY = (y + (y+h)) / 2
    if centerX > rightEdge or centerX < leftEdge:
        return True
    if centerY > topEdge or centerY < bottomEdge:
        return True
    else:
        return False

while(1):
    # Frame and color vars
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Color range in hsv
    lowerBound = np.array([10, 100, 20])
    upperBound = np.array([25, 255, 255])

    # No idea tbh
    kernal = np.ones((5, 5), "uint8")

    # masks
    mask = cv2.inRange(hsv, lowerBound, upperBound)
    mask = cv2.dilate(mask, kernal)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # Contours
    contours, hier = cv2.findContours(mask,
                                      cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)

    # Establish win height, width, and idk
    winH, winW, winC = frame.shape
    # !DEBUG
    # print(winW, winH)
    if len(contours) != 0:
        # !DEBUG
        # cv2.drawContours(frame, contours, 0, (0, 255, 0), 3)
        # C is our largest contour (the fish)
        c = max(contours, key=cv2.contourArea)
        # Size of contour
        area = cv2.contourArea(c)
        if area > 500:
            # Establishes coordinates (x, y) and dimensions (w, h) of our fish's bounding rectangle
            x, y, w, h = cv2.boundingRect(c)
            # Useful shorthands
            centerX = (x + (x+w)) / 2
            centerY = (y + (y+h)) / 2
            centerH = winH / 2
            centerW = winW / 2
            # I have to use these vars for angle idk why
            point1 = (centerW, centerH)
            point2 = (centerX, centerY)

            # Draws our bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 5)

            angle = angleBetween(point1, point2)
            dir = determineDir(angle)
            # !DEBUG
            # print(dir, np.round(angle))

            # Draws line from center to fish
            cv2.line(frame, (int(centerW), int(centerH)), (int(centerX), int(centerY)), (0, 255, 0), 5)
            # Establishes a ratio so the bounding box is proportionate
            # Use if wanted
            # gcd = np.gcd(winW, winH)
            # wRatio = winW / gcd 
            # hRatio = winH / gcd
            # paddingWidth = padding * (wRatio * 0.1)
            # paddingHeight = padding * (hRatio * 0.1)

            # Center of window
            centerW, centerH = winW / 2, winH / 2
            
            # Edges
            leftEdge = centerW - paddingWidth
            rightEdge = centerW + paddingWidth
            topEdge = centerH + paddingHeight
            bottomEdge = centerH - paddingHeight

            # !DEBUG
            topLeftCenterBounds = (int(leftEdge), int(topEdge))
            bottomRightCenterBounds = (int(rightEdge), int(bottomEdge))

            textDisplayValue = ""
            outBounds = outOfEdge(x, y, w, h, leftEdge, rightEdge, topEdge, bottomEdge)

            if outBounds:
                textDisplayValue = "Out of Bounds"
                inBounds = False
            else:
                textDisplayValue = "In Bounds"
                inBounds = True

            # !DEBUG
            # Center Box 
            cv2.rectangle(frame, topLeftCenterBounds, bottomRightCenterBounds, (0, 255, 0), 5)
            cv2.putText(frame, textDisplayValue, (100, 100), font, 1, (255, 255, 255), 5)

    cv2.imshow('frame', frame)
        # cv2.imshow('mask', mask)
        # cv2.imshow('res', res)

    frameTime = 10
    if cv2.waitKey(frameTime) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break
