# from flask import Flask, render_template, request, flash

import requests
from PIL import Image
import io
import cv2
import numpy as np


#app = Flask(__name__)
#app.secret_key = b'mangomango'
#
##app routing to url
#@app.route("/mango")
#def index():
#    flash("Flashy flashy")
#    return render_template("index.html")

api_key = "pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A"
def main():
    address = "Gertrud-Grunow-Straße 4"
    json = requests.get("https://api.mapbox.com/geocoding/v5/mapbox.places/" + address + ".json?access_token=pk.eyJ1IjoiaWRvbnR3ZWFyYnJhcyIsImEiOiJjbDE1MDFjZWEwdG16M2NzNmxsMDVoc2R5In0.U0rNnBS_rRe1EIQPvbID6A").json()
    lat, long = json["features"][0]["center"]

    zoom = 17.5
    res_x, res_y = 800, 800
    img_req_string = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lat},{long},{zoom}/{res_x}x{res_y}?access_token={api_key}"

    res = requests.get(img_req_string)
    bytes_im = io.BytesIO(res.content)
    img_arr = cv2.cvtColor(np.array(Image.open(bytes_im)), cv2.COLOR_RGB2BGR)
    img = img_arr[:, :, ::-1]
    pil_image = Image.fromarray(img)
    pil_image.show()

def loadImage(map_style, long, lat, zoom, res_x, res_y,mapbox_token):
    mapbox_url = "https://api.mapbox.com/styles/v1/mapbox/" + map_style + "/static/{},{},{}/{}x{}?access_token={}".format(
        long,
        lat,
        zoom,
        res_x,
        res_y,
        mapbox_token)
    print("Trying to get ", mapbox_url)
    img = requests.get(mapbox_url)

    bytes_im = io.BytesIO(img.content)
    img_arr = cv2.cvtColor(np.array(Image.open(bytes_im)), cv2.COLOR_RGB2BGR)
    return img_arr[:, :, ::-1]


if __name__ == "__main__":
  main()


















