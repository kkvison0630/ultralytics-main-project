from ultralytics import YOLO
from PIL import Image
import cv2
import os

model = YOLO(r"C:\ultralytics-main\weights\organ.pt")
results = model.predict(r"D:\WeChat Files\wxid_xu6r6np3v15h22\FileStorage\File\2024-06\straight\3-4-72-BLUE-A-DJ25-ZHQ-XZ_B05.tif",save=True)

# 类别
# class_dict = {
#     0:'head',
#     1:'eye',
#     2:'heart',
#     3:'yolk'
# }
#
# im1 = Image.open(r"C:\ZebraFishxg\0.21xg\0.21xg_segment\1.png")
# results = model.predict(source=im1)  # 保存绘制的图像
# pred_mask_path = r'C:\ultralytics-main\runs\segment\mask'
# os.makedirs(pred_mask_path,exist_ok=True)
#
# results_img = results[0].plot(boxes=False)
# cv2.imwrite(os.path.join(pred_mask_path,'result.png'),results_img)
#
# for result in results:
#     mask_data = result.masks.data
#     for index,mask in enumerate(mask_data):
#         mask=mask.cpu().numpy()*255
#         cv2.imwrite(os.path.join(pred_mask_path,f'{class_dict[int(result.boxes.cls[index].cpu().numpy())]}.png'),mask)
