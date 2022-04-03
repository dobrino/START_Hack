import numpy as np
import cv2
from matplotlib import pyplot as plt
from shapely.geometry import Polygon


def get_area(img_path: str):
    img = cv2.imread(img_path)
    edges = cv2.Canny(img, 100, 200)

    row_indices, col_indices = np.nonzero(edges)
    points = list(zip(row_indices, col_indices))

    poly = Polygon(points)
    x, y = poly.exterior.xy
    plt.plot(x, y, c="red")

    area = poly.area
    print(area)


def separate(img_path: str):
    # Load image, grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread(img_path)
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Find contours
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    # init temp variables and constants
    middle = (400, 400)

    rect_bounds = [cv2.boundingRect(c) for c in contours]
    contour_moments = [cv2.moments(c) for c in contours]
    centroids = [(moments["m10"] // moments["m00"], moments["m01"] // moments["m00"])
                 for moments in contour_moments]
    dists_to_middle = [np.linalg.norm([middle[0] - c_x, middle[1] - c_y])
                       for c_x, c_y in centroids]

    # print cropped patches of each region of interest
    for i, roi_rect in enumerate(rect_bounds):
        x_ur, y_ur, width, height = roi_rect
        roi = original[y_ur:y_ur+height, x_ur:x_ur+width]
        cv2.imwrite(f'ROI_{i}.png', roi)

    # augment the image with a bounding box and a circle around the centroid
    for roi_rect, centroid in zip(rect_bounds, centroids):
        c_x, c_y = centroid
        x_ur, y_ur, width, height = roi_rect
        cv2.rectangle(image, (x_ur, y_ur), (x_ur+width, y_ur+height), (36, 255, 12), 4)
        cv2.circle(image, (c_x, c_y), 10, (320, 159, 22), -1)
    cv2.imwrite('image.png', image)

    closest_roi_to_middle = np.argmin(dists_to_middle)

