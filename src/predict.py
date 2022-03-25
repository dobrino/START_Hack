from nn import get_model
import tensorflow as tf
import cv2
import numpy as np
import matplotlib.pyplot as plt


weights_path = "./../data/weights/weights.hdf5"

def predict(img_path):
    model = get_model()
    model.compile(optimizer=tf.keras.optimizers.RMSprop(lr=0.0001), loss='mse', metrics=['mae'])

    model.load_weights(weights_path)

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    img = cv2.filter2D(img, -1, kernel)
    img = cv2.resize(img, (256, 256)) / 255

    testimg = img.reshape(1, 256, 256, 3)
    pred = model.predict(testimg)
    plt.figure(figsize=(10,5))
    plt.subplot(1,2,1)
    plt.axis('off')
    plt.title('Prediction', fontsize=20)
    plt.imshow(pred.reshape((256,  256)), cmap='gray')
    plt.show()
