import json

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

print(images)

file.close()