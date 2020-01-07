"""
TF2.0系で積極実行した場合のみTFreordのイテレーションが可能なのでこのコードを実行する場合は2.0系で実行する
"""
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
tf.enable_eager_execution()
def image_show(data, name, layout, cmap=None):
  """Show an image."""
  #print(type(data))
  plt.subplot(*layout)
  plt.imshow(tf.image.decode_jpeg(data), cmap=cmap)
  plt.title(name)
  plt.grid(False)
  plt.axis('off')

if __name__ == "__main__":
    FILENAME = "C:/Users/Akito/Desktop/waymo/segment-10241508783381919015_2889_360_2909_360_with_camera_labels.tfrecord"
    dataset =tf.data.TFRecordDataset(FILENAME)
    frames = []
    print(dataset)
    for data in dataset:
        frame = open_dataset.Frame()
        frame.ParseFromString(bytearray(data.numpy()))
        frames.append(frame)
    print(len(frames))
    plt.figure(figsize=(25, 20))
    frame = frames[100]
    for index, image in enumerate(frame.images):
        image_show(image.image, open_dataset.CameraName.Name.Name(image.name),[3, 2, index+1])