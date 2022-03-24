from asyncore import read
from cProfile import label
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
        x_points = image["regions"][0]["shape_attributes"]["all_points_x"]
        y_points = image["regions"][0]["shape_attributes"]["all_points_y"]
        images[filename] = (x_points, y_points)

    file.close()

    return images

images = read_json()

labeled_dir = "./../data/labeled/"
unlabeled_dir = "./../data/unlabeled/"

for img in images:
    filename = img
    image = cv2.imread(os.path.join(unlabeled_dir, filename))
    
    dimensions = image.shape
    print(dimensions)
    (mask_x, mask_y) = images[filename]
    print(mask_x)
    print(mask_y)

    pts = np.array([[mask_x[0], mask_y[0]],
        [mask_x[1], mask_y[1]],
        [mask_x[2], mask_y[2]],
        [mask_x[3], mask_y[3]]], np.int32)
    
    fill = cv2.rectangle(image, (0,0), (800,800), (255,255,255),-1)

    rect = cv2.fillPoly(fill, [pts], 0)

    cv2.imwrite(os.path.join(labeled_dir, filename), rect)