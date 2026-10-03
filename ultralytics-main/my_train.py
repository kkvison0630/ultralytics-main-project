'''
实例分割训练
'''
from ultralytics import YOLO
#程序中链接了多个 OpenMP 运行时库的副本
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

#train
model = YOLO(r'C:/ultralytics-main/ultralytics/cfg/models/v8/yolov8-seg.yaml').load(r'C:\Users\JP_Wang\Documents\WeChat Files\wxid_xu6r6np3v15h22\FileStorage\File\2024-06\fish_body\weights\best.pt')  # build from YAML and transfer weights

# Train the model
model.train(data=r'C:/ultralytics-main/ultralytics/cfg/datasets/coco128-seg.yaml', epochs=100, batch=2, lr0=0.01, workers=0)