"""This module provides a rooftop segmentation model."""

from typing import Tuple
from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import \
    Conv2D, BatchNormalization, Activation, MaxPool2D, \
    UpSampling2D, Concatenate, Layer


def _conv_block(depth: int, filters: int, kernel: Tuple[int, int]=(3, 3)) -> Layer:
    block = Sequential()

    for _ in range(depth):
        block.add(Conv2D(filters, kernel, padding='same'))
        block.add(BatchNormalization())
        block.add(Activation('relu'))

    return block


class RoofSegmentationModel(Model):

    def __init__(self, num_classes: int=1):
        super(RoofSegmentationModel, self).__init__()
        self.down_conv_0 = _conv_block(depth=2, filters=32)
        self.down_conv_1 = _conv_block(depth=2, filters=64)
        self.down_conv_2 = _conv_block(depth=2, filters=128)
        self.down_conv_3 = _conv_block(depth=2, filters=256)
        self.down_conv_4 = _conv_block(depth=2, filters=512)
        self.down_conv_5 = _conv_block(depth=2, filters=1024)
        self.up_conv_4 = _conv_block(depth=2, filters=512)
        self.up_conv_3 = _conv_block(depth=2, filters=256)
        self.up_conv_2 = _conv_block(depth=2, filters=128)
        self.up_conv_1 = _conv_block(depth=2, filters=64)
        self.up_conv_0 = _conv_block(depth=2, filters=32)
        self.grayscale_segment = Conv2D(num_classes, (1, 1), activation='sigmoid')
        self.pool = MaxPool2D((2, 2), strides=(2, 2))
        self.up = UpSampling2D((2, 2), strides=(2, 2))
        self.concat = Concatenate(axis=3)

    def call(self, input, training: bool=False):
        # downsampling
        down0 = self.down_conv_0(input)
        down1 = self.down_conv_1(self.pool(down0))
        down2 = self.down_conv_2(self.pool(down1))
        down3 = self.down_conv_3(self.pool(down2))
        down4 = self.down_conv_4(self.pool(down3))
        center = self.down_conv_5(self.pool(down4))

        # upsampling + concat
        up4 = self.up_conv_4(self.concat(self.up(center), down4))
        up3 = self.up_conv_4(self.concat(self.up(up4), down3))
        up2 = self.up_conv_4(self.concat(self.up(up3), down2))
        up1 = self.up_conv_4(self.concat(self.up(up2), down1))
        up0 = self.up_conv_4(self.concat(self.up(up1), down0))

        # grayscale segmentation
        seg_out = self.grayscale_segment(up0)
        return seg_out
