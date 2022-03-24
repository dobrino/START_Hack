from flask import Flask, render_template, request, flash

import requests
from PIL import Image
import io
import cv2
import numpy as np
from sympy import Polygon, Point
import calculations as c
import random


def area(polygons):
    closest_polygon = polygons[closest_poly(polygons)]
    return closest_polygon.area


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
    pil_image.show()
    return img


# app = Flask(__name__)
# app.secret_key = b'mangomango'
#
##app routing to url
# @app.route("/mango")
# def index():
#    flash("Flashy flashy")
#    return render_template("index.html")

api_key = "pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A"


def main():
    address = input('Enter Address:')
    img = generate_image(address)

    # feed img to segmentation model
    # process result through area function

    area = random.randrange(1, 1000)
    print(f"determined Area: {area}")
    self_consumption_ratio = .5  # input("Enter predicted self_need ratio: ")

    print(f"Peak Power of Solar Panel System on Roof: {c.get_peak_power(area)} kW")
    print(f"Yearly energy Output: {c.get_energy_output(area)} kWh")
    print(f"Yearly revenue in Euro: Example with 25% self consumption: {round(c.get_yearly_revenue(area, .25), 2)}€")
    print(f"Yearly revenue in Euro: Example with 30% self consumption: {round(c.get_yearly_revenue(area, .3), 2)}€")
    print(f"Yearly revenue in Euro: Example with 50% self consumption: {round(c.get_yearly_revenue(area, .5),2)}€")
    print(f"Yearly revenue in Euro: Example with 100% self consumption: {round(c.get_yearly_revenue(area, 1),2)}€")
    print(
        f"Installation costs/Initial investment with {self_consumption_ratio * 100}% self_consumption: {round(c.get_initial_investment_costs(area),2)}€")
    print(f"Break even after {round(c.get_break_even_time(area, float(self_consumption_ratio)), 2)} years. Yay!")



if __name__ == "__main__":
    main()
