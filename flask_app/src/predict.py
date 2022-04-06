from typing import Tuple

import cv2
import numpy as np

from tensorflow.keras import Model
from tensorflow.keras.models import load_model


def load_rooftop_segmentation_model(input_shape: Tuple[int, int, int]=(256, 256, 3)) -> Model:
    model: Model = load_model('/model/model_with_weights.hdf5')
    height, width, channels = input_shape
    model.build([None, height, width, channels])
    return model


def load_image(img_path: str):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    img = cv2.filter2D(img, -1, kernel)
    img = cv2.resize(img, (256, 256)) / 255
    return img


def segment_image(img_path: str):
    # TODO: cache the pre-trained model (only load once)
    model = load_rooftop_segmentation_model()
    img = load_image(img_path)
    input_img = np.expand_dims(img, axis=0) # = img.reshape(1, 256, 256, 3)
    seg_img = np.squeeze(model(input_img).numpy())
    assert img.shape == seg_img.shape
    cv2.imwrite("pred.png", seg_img)
