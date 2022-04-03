# use official python image from DockerHub
FROM python:3.8

# install OpenCV dependencies
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && apt-get clean

# install pip requirements
ADD ./requirements.txt .
RUN python -m pip install pip --upgrade && \
    python -m pip install -r requirements.txt

# copy flask app
WORKDIR /flask_app
ADD ./flask_app .

# define service entrypoint to run the flask app
ENTRYPOINT ["python", "testing123.py"]
