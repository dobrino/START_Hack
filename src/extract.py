import numpy as np
import cv2
from matplotlib import pyplot as plt
#import sympy
from shapely.geometry import Polygon



def getArea(img_path):
    img = cv2.imread(img_path)
    edges = cv2.Canny(img, 100, 200)

    row_indices, col_indices = np.nonzero(edges)
    points = list(zip(row_indices, col_indices))

    poly = Polygon(points)
    x, y = poly.exterior.xy
    plt.plot(x, y, c="red")
    # plt.show()

    area = poly.area
    print(area)

def separate(path):
    # Load image, grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread(path)
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Find contours
    ROI_number = 0
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    #init temp variables and constants
    minimum_distance = 800
    middle = (400,400)
    middle_poly_index = 0
    

    for c in cnts:
        # Obtain bounding rectangle to get measurements
        x,y,w,h = cv2.boundingRect(c)

        # Find centroid
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        # Crop and save ROI
        ROI = original[y:y+h, x:x+w]
        cv2.imwrite('ROI_{}.png'.format(ROI_number), ROI)
        ROI_number += 1

        # Draw the contour and center of the shape on the image
        cv2.rectangle(image,(x,y),(x+w,y+h),(36,255,12), 4)
        cv2.circle(image, (cX, cY), 10, (320, 159, 22), -1) 

        tmp_dist = np.linalg.norm(middle-(cX,cY))
        if tmp_dist < minimum_distance:
            middle_poly_index = c
            minimum_distance = tmp_dist

    cv2.imwrite('image.png', image)


