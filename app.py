from flask import Flask, render_template, request, flash

import requests
from PIL import Image
import io
import cv2
import numpy as np
from sympy import Polygon, Point
import calculations as c
import random


api_key = "pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A"


def closest_poly(polygons): #devide area by 9.61
    middle = Point(400,400)
    for i in range(len(polygons)):
        if polygons[i].encloses_point(middle):
            print("Polgyon " + str(i) + " encloses the middle!")
            return i
    min_distance = polygons[0].distance(middle)
    closest_polygon_index = 0
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
    pil_image.show()
    return img


def calculate_stats():
    address = "Gertrud-Grunow-Straße 4"  # input('Enter Address:')
    img = generate_image(address)

    # feed img to segmentation model
    # process result through area function

    temparea = random.randrange(1, 1000)
    print(f"determined Area: {temparea}")
    self_consumption_ratio = .5  # input("Enter predicted self_need ratio: ")

    # c.print(area, self_consumption_ratio)


def main():
    print('empty main')

if __name__ == "__main__":
    main()
