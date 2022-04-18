# use official python image from DockerHub
FROM python:3.8

# install OpenCV dependencies
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && apt-get clean

# install pip requirements
ADD ./requirements.txt .
RUN python -m pip install pip --upgrade && \
    python -m pip install -r requirements.txt

# copy pre-trained segmentation model
ADD ./segmentation/model_with_weights.hdf5 /model/

# copy flask app
WORKDIR /flask_app
ADD ./flask_app .

# run the linter to enforce the PEP coding style
WORKDIR /
RUN pylint flask_app --extension-pkg-whitelist=cv2 --fail-under=9.5
WORKDIR /flask_app

# define service entrypoint to run the flask app
ENTRYPOINT ["python", "webservice.py"]
