"""
TF2.0系で積極実行した場合のみTFreordのイテレーションが可能なのでこのコードを実行する場合は2.0系で実行する
"""
import sys
import os
import imp
import tensorflow as tf
import math
import numpy as np
import itertools
import matplotlib.pyplot as plt
from waymo_open_dataset.utils import range_image_utils
from waymo_open_dataset.utils import transform_utils
from waymo_open_dataset import dataset_pb2 as open_dataset
import glob
import PIL
import datetime
tf.enable_eager_execution()
sys.setrecursionlimit(10000)
def image_show(data, name, cmap=None):
    """Show an image."""
    #print(type(data))
    plt.figure()
    plt.imshow(tf.image.decode_jpeg(data), cmap=cmap)
    #plt.title(name)
    plt.grid(False)
    plt.axis('off')
    plt.savefig('figure/figure{0:%Y%m%d%H%M%S}.jpg'.format(datetime.datetime.now()))
    #plt.show()

if __name__ == "__main__":
    args =sys.argv
    FILENAME="F:/waymo-dataset/training_0000/segment-10206293520369375008_2796_800_2816_800_with_camera_labels.tfrecord"
    FILES = "F:/waymo-dataset/"+args[1]+"/*.tfrecord"
    print(glob.glob(FILES))
    dataset =tf.data.TFRecordDataset(FILENAME)
    frames = []
    print(dataset)
    for data in dataset:
        frame = open_dataset.Frame()
        frame.ParseFromString(bytearray(data.numpy()))
        frames.append(frame)
    print(len(frames))
    frame = frames[100]
    for index,frame in enumerate(frames):
      image_show(frame.images[0].image,index)