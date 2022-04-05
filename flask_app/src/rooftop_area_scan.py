"""This module provides an entrypoint for measuring
a rooftop's surface area, given its postal address"""

from typing import Tuple, List
import requests
import io
from PIL import Image

from shapely.geometry import Polygon, Point

from src.extract import get_area, separate
from src.predict import segment_image


def area(polygons):
    closest_polygon = polygons[closest_poly(polygons)]
    return closest_polygon.area / 9.61 # TODO: what does 9.61 mean???


def closest_poly(polygons: List[Polygon]):
    middle = Point(400, 400)
    for i in range(len(polygons)):
        if polygons[i].contains(middle):
            return i
    min_distance = polygons[1].distance(middle)
    closest_polygon_index = 1
    for x in range(len(polygons)):
        if polygons[x].distance(middle) < min_distance:
            min_distance = polygons[x].distance(middle)
            closest_polygon_index = x
    return closest_polygon_index


def query_coordinates(address: str, api_token: str) -> Tuple[float, float]:
    query = f"{address}.json?access_token={api_token}"
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}"
    json = requests.get(url).json()
    lat, long = json["features"][0]["center"]
    return lat, long


def download_satellite_image_at_geopos(geo_pos: Tuple[float, float], api_token: str) -> Image.Image:
    zoom = 17.5
    res_x, res_y = 800, 800
    lat, long = geo_pos

    query = f'{lat},{long},{zoom}/{res_x}x{res_y}?access_token={api_token}'
    img_req_string = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{query}"
    print(f"requesting satellite image from URL'{img_req_string}'")

    res = requests.get(img_req_string)
    bytes_im = io.BytesIO(res.content)
    return Image.open(bytes_im)


def generate_image(address: str, api_token: str) -> Image.Image:
    geo_pos = query_coordinates(address, api_token)
    pil_image = download_satellite_image_at_geopos(geo_pos, api_token)

    # TODO: why conversion from RGB to BGR and backwards again?
    # img_arr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    # img = img_arr[:, :, ::-1] # BGR to RGB
    # pil_image = Image.fromarray(img)

    return pil_image


def calculate_rooftop_area(address: str) -> Tuple[float, Image.Image]:
    api_token = "pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A"
    temp_file_path = "tmp.png"

    # TODO: consider keeping the images in memory without having to reload them from file
    #       -> abstract away how the images are loaded into RAM from the processing logic

    img = generate_image(address, api_token)
    img.save(temp_file_path)

    # feed img to segmentation model
    # process result through area function
    segment_image(temp_file_path)
    separate(temp_file_path)
    area = get_area("ROI_0.png")
    return area, img


if __name__ == "__main__":
    address = "Gertrud-Grunow-Straße 4"
    roof_area, _ = calculate_rooftop_area(address)
    if area is None:
        print("oops, something went wrong ...")
    print(f"the house located at {address} has a rooftop surface area of {roof_area} m^2")
