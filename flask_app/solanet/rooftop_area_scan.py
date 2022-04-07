"""This module provides an entrypoint for measuring
a rooftop's surface area, given its postal address"""

import io
import requests
from math import dist
from dataclasses import dataclass, field
from typing import Tuple
from PIL import Image

import cv2
import numpy as np
from tensorflow.keras import Model
from tensorflow.keras.models import load_model
from shapely.geometry import Polygon


@dataclass
class SatelliteImageProvider:
    """Representing a service for requesting satellite images at given postal addresses."""

    api_token: str = "pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A"
    coord_api_base_url: str = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    satellite_api_base_url: str = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static"
    img_size: Tuple[int, int] = field(default_factory=lambda: (800, 800))
    zoom: float = 17.5

    def query_coordinates(self, address: str) -> Tuple[float, float]:
        url = f"{self.coord_api_base_url}/{address}.json?access_token={self.api_token}"
        json = requests.get(url).json()
        lat, long = json["features"][0]["center"]
        return lat, long

    def download_satellite_image(self, geo_pos: Tuple[float, float]) -> np.ndarray:
        lat, long = geo_pos
        res_x, res_y = self.img_size
        query = f'{lat},{long},{self.zoom}/{res_x}x{res_y}?access_token={self.api_token}'
        img_req_string = f"{self.satellite_api_base_url}/{query}"
        print(f"requesting satellite image from URL'{img_req_string}'")

        res = requests.get(img_req_string)
        bytes_im = io.BytesIO(res.content)
        return np.array(Image.open(bytes_im))


@dataclass
class RooftopSegmentation:
    model: Model = field(init=False)
    input_shape: Tuple[int, int, int] = field(default_factory=lambda: (256, 256, 3))
    filter_kernel: np.ndarray = field(default_factory=lambda:
        np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
    model_path: str = field(default_factory=lambda: '/model/model_with_weights.hdf5')

    def __post_init__(self):
        self.model = load_model(self.model_path)
        height, width, channels = self.input_shape
        self.model.build([None, height, width, channels])

    def segment_image(self, img: np.ndarray):
        img = cv2.filter2D(img, -1, self.filter_kernel)
        height, width, _ = self.input_shape
        img = cv2.resize(img, (height, width)) / 255

        input_img = np.expand_dims(img, axis=0)
        pred = self.model(input_img)
        return (np.squeeze(pred.numpy()) * 255).astype(np.uint8)


@dataclass
class RooftopDetection:
    # TODO: put the hyperparams here -> software-as-code param optimization

    def separate_rooftop_roi(self, seg_img: np.ndarray):
        # apply Gaussian blur and Otsu's threshold, then find contours
        original = seg_img.copy()
        blur = cv2.GaussianBlur(seg_img, (3, 3), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        # define regions of interest from contours
        rect_bounds = [cv2.boundingRect(c) for c in contours]
        rois = [original[y_ur:y_ur+height, x_ur:x_ur+width]
                for x_ur, y_ur, width, height in rect_bounds]

        # choose the ROI that's closest to the middle of the image
        middle = (400, 400)
        centroids = [(x_ur + width // 2, y_ur + height // 2)
                     for x_ur, y_ur, width, height in rect_bounds]
        dists_to_middle = [dist(c, middle) for c in centroids]
        return rois[np.argmin(dists_to_middle)]

    def get_segmented_area(self, roi_img: np.ndarray) -> float:
        # TODO: check if canny filter works on grayscale images
        edges = cv2.Canny(roi_img, 100, 200)
        row_indices, col_indices = np.nonzero(edges)
        points = list(zip(row_indices, col_indices))
        poly = Polygon(points)
        return poly.area


@dataclass
class RooftopAreaScanner:
    satellite_imgs: SatelliteImageProvider = field(default_factory=lambda: SatelliteImageProvider())
    segmentation: RooftopSegmentation = field(default_factory=lambda: RooftopSegmentation())
    detection: RooftopDetection = field(default_factory=lambda: RooftopDetection())
    debug: bool = field(default_factory=lambda: False)

    def calculate_rooftop_area(self, address: str) -> Tuple[float, np.ndarray]:
        geo_pos = self.satellite_imgs.query_coordinates(address)
        sat_img = self.satellite_imgs.download_satellite_image(geo_pos)

        if self.debug:
            cv2.imshow('original', sat_img)
            cv2.waitKey(5000)

        seg_img = self.segmentation.segment_image(sat_img)
        if self.debug:
            cv2.imshow('segmented_roofs', seg_img)
            cv2.waitKey(5000)

        roi_img = self.detection.separate_rooftop_roi(seg_img)
        if self.debug:
            cv2.imshow('selected_roof', roi_img)
            cv2.waitKey(5000)

        area = self.detection.get_segmented_area(roi_img)
        return area, sat_img


if __name__ == "__main__":
    # TODO: think of transforming this into one or more unit tests
    address = "Gertrud-Grunow-Straße 4"
    debug_model_path = '../../segmentation/model_with_weights.hdf5'
    roof_calc = RooftopAreaScanner(segmentation=RooftopSegmentation(model_path=debug_model_path), debug=True)
    roof_area, _ = roof_calc.calculate_rooftop_area(address)
    if roof_area is None:
        print("oops, something went wrong ...")
    print(f"the house located at {address} has a rooftop surface area of {roof_area} m^2")
