"""This module provides an entrypoint for measuring
a rooftop's surface area, given its postal address"""

import io
from math import dist
from dataclasses import dataclass, field
from typing import Tuple

import requests
from PIL import Image

import cv2
import numpy as np
from shapely.geometry import Polygon

# pylint: disable=no-name-in-module,import-error
from tensorflow.keras import Model
from tensorflow.keras.models import load_model
# pylint: enable=no-name-in-module,import-error


@dataclass
class SatelliteImageProvider:
    """Representing a service for requesting satellite images at given postal addresses."""

    # TODO: transform the api token into a secret variable
    api_token: str = "pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A"
    coord_api_base_url: str = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    satellite_api_base_url: str = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static"
    img_size: Tuple[int, int] = field(default=(800, 800))
    zoom: float = 17.5

    def query_coordinates(self, address: str) -> Tuple[float, float]:
        """Retrieve the coordinates belonging to the given postal address."""

        url = f"{self.coord_api_base_url}/{address}.json?access_token={self.api_token}"
        json = requests.get(url).json()
        lat, long = json["features"][0]["center"]
        return lat, long

    def download_satellite_image(self, coords: Tuple[float, float]) -> np.ndarray:
        """Download the satellite camera snapshot at the given coordinates."""

        lat, long = coords
        res_x, res_y = self.img_size
        query = f'{lat},{long},{self.zoom}/{res_x}x{res_y}?access_token={self.api_token}'
        img_req_string = f"{self.satellite_api_base_url}/{query}"
        print(f"requesting satellite image from URL'{img_req_string}'")

        res = requests.get(img_req_string)
        bytes_im = io.BytesIO(res.content)
        return np.array(Image.open(bytes_im))


@dataclass
class RooftopSegmentation:
    """Representing an image segmentation by neural network."""

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
        """Segment the given RGB image into a grayscale,
        indicating which pixels belong to rooftops."""

        img = cv2.filter2D(img, -1, self.filter_kernel)
        height, width, _ = self.input_shape
        img = cv2.resize(img, (height, width)) / 255

        input_img = np.expand_dims(img, axis=0)
        pred = self.model(input_img)
        return (np.squeeze(pred.numpy()) * 255).astype(np.uint8)


@dataclass
class RooftopDetection:
    """Representing machine learning techniques to determine
    the surface area inside of segmented rooftops images."""

    # TODO: put the hyperparams here -> software-as-code param optimization
    img_size: Tuple[int, int] = field(default=(800, 800))
    canny_bounds: Tuple[float, float] = field(default=(100, 200))
    gaussian_blur_size: Tuple[int, int] = field(default=(3, 3))
    otsu_threshold_range: Tuple[int, int] = field(default=(0, 255))

    def separate_rooftop_roi(self, seg_img: np.ndarray):
        """Detect potential regions of interest and
        choose the one closest to the middle."""

        # apply Gaussian blur and Otsu's threshold, then find contours
        original = seg_img.copy()
        blur = cv2.GaussianBlur(seg_img, self.gaussian_blur_size, 0)
        otsu_low, otsu_high = self.otsu_threshold_range
        otsu_flags = cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        _, thresh = cv2.threshold(blur, otsu_low, otsu_high, otsu_flags)
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        # define regions of interest from contours
        rect_bounds = [cv2.boundingRect(c) for c in contours]
        rois = [original[y_ur:y_ur+height, x_ur:x_ur+width]
                for x_ur, y_ur, width, height in rect_bounds]

        # choose the ROI that's closest to the middle of the image
        middle = (self.img_size[0] // 2, self.img_size[1] // 2)
        centroids = [(x_ur + width // 2, y_ur + height // 2)
                     for x_ur, y_ur, width, height in rect_bounds]
        dists_to_middle = [dist(c, middle) for c in centroids]
        return rois[np.argmin(dists_to_middle)]

    def get_segmented_area(self, roi_img: np.ndarray) -> float:
        """Detect the area contained by the given region of interest."""

        # TODO: check if canny filter works on grayscale images
        lower, upper = self.canny_bounds
        edges = cv2.Canny(roi_img, lower, upper)
        row_indices, col_indices = np.nonzero(edges)
        points = list(zip(row_indices, col_indices))
        poly = Polygon(points)
        return poly.area


@dataclass
class RooftopAreaScanner:
    """Representing a service that's capable of computing
    the rooftop area, given a house's postal address."""

    satellite_imgs: SatelliteImageProvider = field(default=SatelliteImageProvider())
    segmentation: RooftopSegmentation = field(default=RooftopSegmentation())
    detection: RooftopDetection = field(default=RooftopDetection())
    debug: bool = field(default=False)

    def calculate_rooftop_area(self, address: str) -> Tuple[float, np.ndarray]:
        """Calculate the rooftop area, given the house's postal address."""

        coords = self.satellite_imgs.query_coordinates(address)
        sat_img = self.satellite_imgs.download_satellite_image(coords)

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
    ADDRESS = "Gertrud-Grunow-Straße 4"
    DEBUG_MODEL_PATH = '../../segmentation/model_with_weights.hdf5'
    seg = RooftopSegmentation(model_path=DEBUG_MODEL_PATH)
    roof_calc = RooftopAreaScanner(segmentation=seg, debug=True)
    roof_area, _ = roof_calc.calculate_rooftop_area("Gertrud-Grunow-Straße 4")
    if roof_area is None:
        print("oops, something went wrong ...")
    print(f"the house located at {ADDRESS} has a rooftop surface area of {roof_area} m^2")
