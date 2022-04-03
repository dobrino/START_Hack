# START_Hack
Alles Mango

TODO: add an about section describing what the project does

TODO: add a link to the presentation

TODO: add details about training the model

## Tools Setup

```sh
sudo apt-get update && sudo apt-get install -y docker.io docker-compose curl git
sudo usermod -aG docker $USER && reboot
# WARNING: the last command will reboot your PC and close all running apps
```

## Build + Run

```sh
git clone https://github.com/dobrino/START_Hack
cd START_Hack
docker-compose up --build
```
