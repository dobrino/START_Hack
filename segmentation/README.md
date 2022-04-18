
# Segmentation AI Training

## NVIDIA Docker Setup
Install the proprietary NVIDIA driver for your system (e.g. Ubuntu 20.04).

*Note: Don't be another guy learning it the hard way. Use the proprietary driver!*

![](./nvidia-driver-selection.png)

Then, run following commands to set up NVIDIA Docker, granting your Docker
containers access to the GPU. That way, you will be set up for GPU-empowered
AI development within minutes. No toxic CUDA / cuDNN setup anymore.

```sh
# register the NVIDIA Docker PPA as apt source
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list \
        | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# install NVIDIA Docker from the official NVIDIA PPA (will reboot afterwards)
sudo apt-get update && sudo apt-get install -y nvidia-docker2 && reboot
```

See the [official documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#setting-up-nvidia-container-toolkit)
for further information.

## Run Training within GPU-Empowered Jupyter Server
After NVIDIA Docker is set up, you can launch a GPU-empowered Jupyter server
with TensorFlow tools pre-installed (official TensorFlow DockerHub image).

```sh
docker run -it --rm -v $PWD:/tf/notebooks -p 8888:8888 \
    --runtime=nvidia  --gpus all --security-opt seccomp=unconfined \
    tensorflow/tensorflow:latest-gpu-jupyter
```

Click the link that's written to console to open Jupyter inside your browser.
Then, choose 'notebooks' and 'training.ipynb' to open the training notebook.
Executing the notebook once again will update the rooftop segmentation model.

## Model Architecture
TODO: outline how the segmentation model works
