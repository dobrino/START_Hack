import json
import cv2
import os
import numpy as np


def read_json():
    with open('./../training.json', 'r') as file:
        data = file.read()

    images = {}
    obj = json.loads(data)

    for o in obj:
        image = obj[o]
        filename = image["filename"]
        coords = []
        count = 0
        for reg in image["regions"]:
            x_points = image["regions"][count]["shape_attributes"]["all_points_x"]
            y_points = image["regions"][count]["shape_attributes"]["all_points_y"]

            coords.append((x_points, y_points))
            count = count + 1

        images[filename] = coords

    file.close()

    return images


images = read_json()

labeled_dir = "./../data/labeled/"
unlabeled_dir = "./../data/unlabeled/"

for img in images:
    filename = img
    image = cv2.imread(os.path.join(unlabeled_dir, filename))

    fill = cv2.rectangle(image, (0, 0), (800, 800), (255, 255, 255), -1)

    dimensions = image.shape
    print(dimensions)
    coords = images[filename]  # array of tuples

    for coord in coords:
        (mask_x, mask_y) = coord
        pts = []
        count = 0
        for x in mask_x:
            pts.append([mask_x[count], mask_y[count]])
            count = count + 1

        fill = cv2.fillPoly(fill, [np.array(pts, np.int32)], 0)

    cv2.imwrite(os.path.join(labeled_dir, filename), fill)
