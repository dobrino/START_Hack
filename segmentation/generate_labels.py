import os
import json
from typing import Dict, List, Tuple

import cv2
import numpy as np


def load_seg_regions_json(labels_file: str) -> Dict[str, List[List[Tuple[float, float]]]]:

    with open(labels_file, 'r') as file:
        labels_json = json.load(file)
        images: Dict[str, List[List[Tuple[float, float]]]] = {}

        for label_key in labels_json:
            image = labels_json[label_key]
            filename: str = image["filename"]
            region_polys = [list(zip(region["shape_attributes"]["all_points_x"], 
                                     region["shape_attributes"]["all_points_y"]))
                            for region in image["regions"]]
            images[filename] = region_polys

    return images


def generate_segmentation_labels(images: Dict[str, List[List[Tuple[float, float]]]],
                                 labeled_dir: str, unlabeled_dir: str):

    for filename in images:
        unlabeled_img_path = os.path.join(unlabeled_dir, filename)
        image = cv2.imread(unlabeled_img_path)
        fill = cv2.rectangle(image, (0, 0), (800, 800), (255, 255, 255), -1)

        polygons = images[filename]
        for polygon in polygons:
            fill = cv2.fillPoly(fill, [np.array(polygon, np.int32)], 0)

        labeled_img_path = os.path.join(labeled_dir, filename)
        cv2.imwrite(labeled_img_path, fill)


def main():
    labels_json = 'dataset/labels.json'
    labeled_dir = "dataset/labeled/"
    unlabeled_dir = "dataset/unlabeled/"

    if not os.path.exists(labeled_dir):
        os.mkdir(labeled_dir)

    image_polys = load_seg_regions_json(labels_json)
    generate_segmentation_labels(image_polys, labeled_dir, unlabeled_dir)


if __name__ == '__main__':
    main()
