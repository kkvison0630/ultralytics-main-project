import os
import json
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import matplotlib
matplotlib.use( "TkAgg")
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


if __name__ == '__main__':
    model = YOLO(r'C:\Users\JP_Wang\Documents\WeChat Files\wxid_xu6r6np3v15h22\FileStorage\File\2024-06\fish_enhance\weights\best.pt')
    metrics = model.val(data=r'C:\ultralytics-main\dataset.yaml')
