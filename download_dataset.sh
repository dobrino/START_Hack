#!/bin/bash
set -e

DATASET_URL=https://syncandshare.lrz.de/dl/fiBqNKYLExyAnE9MBTL9qeNH/D%C3%A4cher_Industrie.dir
wget $DATASET_URL -O dataset.zip

if [ -d dataset/img ]; then
    rm -rf dataset/img
fi
mkdir -p dataset/img

unzip -q dataset.zip -d dataset/img
rm -rf dataset.zip
