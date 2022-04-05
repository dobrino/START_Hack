# START_Hack - SolaNet

TODO: add some cool badges to make the project look professional

## About
TODO: outline what the project is about

For further information, have a look at our [presentation](./SolaNet_Presentation.pdf).

## Tools Setup

```sh
sudo apt-get update && sudo apt-get install -y docker.io docker-compose curl git
sudo usermod -aG docker $USER && reboot
# WARNING: the last command will reboot your PC and close all running apps
```

## AI Training
TODO: add details about training the model

## Build + Run

```sh
git clone https://github.com/dobrino/START_Hack
cd START_Hack
docker-compose up --build
```

## Test API Endpoint

```sh
ADDRESS="Gertrud-Grunow-Straße 4"
API_ENDPOINT_URL="http://localhost:5000"
curl -X POST -F "nm=$ADDRESS" $API_ENDPOINT_URL
```

TODO: add a license
