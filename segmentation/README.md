
# Segmentation AI Training

## NVIDIA Docker Setup

Install the proprietary NVIDIA driver for your system (e.g. Ubuntu 20.04).
Then, run following commands to set up Docker + NVIDIA Docker.

```sh
# install cURL, Docker and Docker-Compose
sudo apt-get update && sudo apt-get install -y curl docker.io docker-compose

# register the NVIDIA Docker PPA as apt source
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list \
        | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# install NVIDIA Docker from the official NVIDIA PPA
sudo apt-get update && sudo apt-get install -y nvidia-docker2

# allow non-root users to work with Docker (requires a reboot)
sudo usermod -aG docker $USER && reboot
```

## Prepare Dataset

```sh
./download_dataset.sh
python3 generate_labels.py
```

## Run GPU-Empowered Jupyter Server

```sh
docker run -it --rm -v $PWD:/tf/notebooks -p 8888:8888 \
    --runtime=nvidia  --gpus all --security-opt seccomp=unconfined \
    tensorflow/tensorflow:latest-gpu-jupyter
```

Execute the training notebook to update the model.
