# Preprocessing on Dataset
from PIL import Image
import numpy as np
import cv2
import random
import os
import glob
import logging
import time
import datetime
logger = logging.getLogger(__name__)
def resize_with_padding(image_array, min_size, max_size):
    """
    入ってきた画像を必要な形にパディングする関数
    Args:
    image_array(ndarray):加工される入力画像
    min_size(int):画像の最小サイズ
    max_size(int):画像の最大サイズ
    """
    h, w = image_array.shape[:2]
    window = (0, 0, h, w)
    scale = 1

    scale = max(1, min_size / min(h, w))

    # Adjusting so that not exceeding maximum size.
    image_max = max(h, w)
    if round(image_max * scale) > max_size:
        scale = max_size / image_max
    
    # Reshaping via scale if necessary
    if scale != 1:
        image_array = cv2.resize(image_array, None, fx=scale, fy=scale)
    # Padding
    h, w = image_array.shape[:2]
    top_pad = (max_size - h) // 2
    bottom_pad = max_size - h - top_pad
    left_pad = (max_size - w) // 2
    right_pad = max_size - w - left_pad
    padding = [(top_pad, bottom_pad), (left_pad, right_pad), (0, 0)]
    image_array = np.pad(image_array, padding,
                         mode='constant', constant_values=0)
    # 左上を原点とした座標系で表現する
    window = (top_pad, left_pad, h + top_pad, w + left_pad)

    return image_array, window, scale

def show_images(config, paths):

    gen = DataGenerator(config)
    for path in paths:
        image, bin_mask, masked_image, _ = gen.load_image(path)
        print(bin_mask)
        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.imshow('masked_image', masked_image)
        cv2.waitKey(0)

class DataGenerator:
    """
    Attributes:
    none    
    """
    def __init__(self, config, random_hole=True):
        self.config = config
        self.random_hole = random_hole

    def normalize_image(self, image):
        # Output of the generator is normalized.
        return (image / 127.5) - 1

    def denormalize_image(self, image):
        # Return from 0 to 255 based on generator output (-1 to 1).
        return ((image + 1) * 127.5).astype(np.uint8)

    def load_image(self, path):
        
        """
        Get the input image, binary mask, image cut out with binary mask.
         The mask is random. It must be a mask that can be commonly applied to multiple input images.
        """
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.warn("Image Does not Exist")
            return None, None, None, None

        resized_image, window, _ = resize_with_padding(image,self.config.input_size,self.config.input_size)
        pil_img=Image.fromarray(
        resized_image)
        pil_img.save('resized/resized{0:%Y%m%d%H%M%S}.jpg'.format(datetime.datetime.now()))

        # mask
        y1, x1, y2, x2 = window
        if y2 - y1 < self.config.mask_size or x2 - x1 < self.config.mask_size:
            logger.warn("Cannot mask Please stop this : %s", window)
            return None, None, None, None

        # Area to be masked
        # windowの枠の範囲内で乱数を生成し、その領域をマスクする
        # ここの変数をいじってマスクの位置を白線が頻出する領域に絞りたい
        if self.random_hole:
            y1 = 150
            x1 = 150
        else:
            y1 = y1 + (y2 - y1) // 4
            x1 = x1 + (x2 - x1) // 4
        y2 = y1 + self.config.mask_size
        x2 = x1 + self.config.mask_size
        mask_window = (y1, x1, y2, x2)

        # マスク領域内の穴（マスクビットを立てる領域）
        # マスクされる候補の領域を決定→実際にマスクする領域を決定の流れ。
        # ここからでは実際にマスクされる領域を決定する
        # h,w:マスク領域の大きさ
        # px1,py1:マスク領域の開始地点の座標
        if self.random_hole:
            
            h, w = (50,35)
            py1 = y1
            px1 = x1 
        else:
            h, w = self.config.hole_max, self.config.hole_max
            py1 = y1 + (self.config.mask_size - h) // 2
            px1 = x1 + (self.config.mask_size - w) // 2
        py2 = py1 + h
        px2 = px1 + w

        masked_image = resized_image.copy()
        masked_image[py1:py2 + 1, px1:px2 + 1, :] = 0
        pil_img=Image.fromarray(
        masked_image)
        pil_img.save('masked/masked{0:%Y%m%d%H%M%S}.jpg'.format(datetime.datetime.now()))
        #exit()
        # Binary Mask
        bin_mask = np.zeros(resized_image.shape[0:2])
        bin_mask[py1:py2 + 1, px1:px2 + 1] = 1
        
        return resized_image, bin_mask, masked_image, mask_window

    def generate(self, data_dir, train_generator=True,train_discriminator=True):
        i = 0
        while True:
            # jpgを参照しているので、もしTFrecordを使うのであればここの加工が必要
            paths = glob.glob(os.path.join(data_dir, '*.jpg'))
            # In order to use different images in each thread when training in parallel shuffle
            random.shuffle(paths)
            for path in paths:
                if i == 0:
                    resized_images = []
                    bin_masks = []
                    masked_images = []
                    mask_windows = []

                resized_image, bin_mask, masked_image, mask_window = \
                    self.load_image(path)
                if resized_image is None:
                    continue

                i += 1
                # Normalization
                resized_image = self.normalize_image(resized_image)
                masked_image = self.normalize_image(masked_image)
                resized_images.append(resized_image)
                bin_masks.append(bin_mask)
                masked_images.append(masked_image)
                mask_windows.append(mask_window)

                if i == self.config.batch_size:
                    resized_images = np.array(resized_images)
                    bin_masks = np.array(bin_masks)
                    masked_images = np.array(masked_images)
                    mask_windows = np.array(mask_windows, dtype=np.int32)

                    inputs = [masked_images, bin_masks]
                    targets = []
                    if train_generator:
                        targets.append(resized_images)
                    if train_discriminator:
                        inputs.append(mask_windows)
                        inputs.append(resized_images)
                        # discriminatorの正解データ
                        # networkの実装に合わせて[real, fake]=[1,0]とする
                        targets.append(
                            np.tile([1, 0], (self.config.batch_size, 1)))
                    i = 0
                    yield inputs, targets