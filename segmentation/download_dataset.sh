#!/bin/bash
set -e

DATASET_ROOT=dataset/unlabeled
DATASET_URL=https://syncandshare.lrz.de/dl/fiBqNKYLExyAnE9MBTL9qeNH/D%C3%A4cher_Industrie.dir
wget $DATASET_URL -O dataset.zip

if [ -d $DATASET_ROOT ]; then
    rm -rf $DATASET_ROOT
fi
mkdir -p $DATASET_ROOT

unzip -q dataset.zip -d $DATASET_ROOT
rm -rf dataset.zip
