import requests
from PIL import Image
import io
import cv2
import numpy as np
from sympy import Point
import calculations as c
import random
from src.extract import getArea, separate

from src.predict import predict


api_key = "pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A"


def area(polygons):
    closest_polygon = polygons[closest_poly(polygons)]
    return closest_polygon.area/9.61


def closest_poly(polygons):
    middle = Point(400, 400)
    for i in range(len(polygons)):
        if polygons[i].encloses_point(middle):
            return i
    min_distance = polygons[1].distance(middle)
    closest_polygon_index = 1
    for x in range(len(polygons)):
        if polygons[x].distance(middle) < min_distance:
            min_distance = polygons[x].distance(middle)
            closest_polygon_index = x
    return closest_polygon_index


def generate_image(address):
    json = requests.get(
        "https://api.mapbox.com/geocoding/v5/mapbox.places/" + address + ".json?access_token=pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A").json()
    print(json)
    lat, long = json["features"][0]["center"]
    print(str(long) + ', ' + str(lat))
    zoom = 17.5
    res_x, res_y = 800, 800
    img_req_string = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lat},{long},{zoom}/{res_x}x{res_y}?access_token={api_key}"
    print(img_req_string)
    res = requests.get(img_req_string)
    bytes_im = io.BytesIO(res.content)
    img_arr = cv2.cvtColor(np.array(Image.open(bytes_im)), cv2.COLOR_RGB2BGR)
    img = img_arr[:, :, ::-1]
    pil_image = Image.fromarray(img)
    return pil_image


def calculate_stats():
    address = "Gertrud-Grunow-Straße 4"  # input('Enter Address:')
    img = generate_image(address)

    # feed img to segmentation model
    # process result through area function
    img.save("tmp.png")
    predict("tmp.png")
    separate("tmp.png")
    area = getArea("ROI_0.png")

    if area is None:
        area = random.randrange(1, 1000)
    print(f"determined Area: {area}")


def main():
    calculate_stats()


if __name__ == "__main__":
    main()
