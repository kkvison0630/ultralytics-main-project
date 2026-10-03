from ultralytics import YOLO
import cv2
import os
import numpy as np
import hUtils

# 模型所在路径
AT_model = YOLO(r"../weights/AT.pt")
VE_model = YOLO(r"../weights/VE.pt")

# EXCEL表格存储路径，命名为视频名字
fileName = r'C:\ultralytics-main\test0619.xlsx'

# 预测结果输出文件夹
out_folder = "C:/heart_test0619"
os.makedirs(out_folder,exist_ok=True)

video_folder = r'D:\environmentalPaper\IMAGE'

for i,filename in enumerate(os.listdir(video_folder)):
    # 视频所在路径
    video_path = os.path.join(video_folder,filename)

    # 存储视频单帧文件夹
    clip_folder = os.path.join(video_folder,f'{os.path.basename(video_path).split(".AVI")[0]}-clip')
    os.makedirs(clip_folder,exist_ok=True)

    # 预测结果输出文件夹
    out_folder = os.path.join(video_folder,f'{os.path.basename(video_path).split(".AVI")[0]}-results')
    os.makedirs(out_folder, exist_ok=True)

    # EXCEL表格存储路径，命名为视频名字
    name_str = os.path.basename(video_path).split('.AVI')[0]
    fileName = os.path.join(video_folder,f'{name_str}.xlsx')

    #
    scale = 3.4162

    class_dict = {
        0:'ve',
        1:'at'
    }

    cap = cv2.VideoCapture(video_path)
    flag = 0
    i = 0
    while(cap.isOpened()):
        i += 1
        ret,frame = cap.read()
        flag += 1
        name = str(flag)
        if ret:
            # imgsz根据原图片尺寸调整
            AT_results = AT_model.predict(source=frame,imgsz=np.size(frame,0))
            VE_results = VE_model.predict(source=frame,imgsz=np.size(frame,0))
            cv2.imwrite(os.path.join(clip_folder,name+"_AT.jpg"),AT_results[0].plot(boxes=False))
            cv2.imwrite(os.path.join(clip_folder,name+"_VE.jpg"),VE_results[0].plot(boxes=False))
            save_folder = os.path.join(out_folder,name)
            os.makedirs(save_folder,exist_ok=True)
            area_list = [0, 0]
            for result in AT_results:
                if result.masks is not None and len(result.masks) > 0:
                    mask_data = result.masks.data
                    for index, mask in enumerate(mask_data):
                        mask = mask.cpu().numpy() * 255
                        cv2.imwrite(
                            os.path.join(save_folder, f'AT.png'),
                            mask)
                        mask = cv2.imread(
                            os.path.join(save_folder, f'AT.png'))
                        img = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)[1]
                        area = 0
                        contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
                        for j in range(len(contours)):
                            area += cv2.contourArea(contours[j])
                        area_list[1] = area

            for result in VE_results:
                if result.masks is not None and len(result.masks) > 0:
                    mask_data = result.masks.data
                    for index, mask in enumerate(mask_data):
                        mask = mask.cpu().numpy() * 255
                        cv2.imwrite(
                            os.path.join(save_folder, f'VE.png'),
                            mask)
                        mask = cv2.imread(
                            os.path.join(save_folder, f'VE.png'))
                        img = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)[1]
                        area = 0
                        contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
                        for j in range(len(contours)):
                            area += cv2.contourArea(contours[j])
                        area_list[0] = area

            ve_area = area_list[0]
            at_area = area_list[1]

            # 获取心室心房的长度以及宽度
            ve_path = os.path.join(save_folder,"VE.png")
            if os.path.exists(ve_path):
                if ve_area != 0:
                    vL = hUtils.find_object_length(ve_path)
                    vW = hUtils.find_object_width(ve_path)
                else:
                    vL = 0
                    vW = 0
            else:
                vL = 0
                vW = 0

            at_path = os.path.join(save_folder,"AT.png")
            if os.path.exists(at_path):
                if at_area != 0:
                    aL = hUtils.find_object_length(at_path)
                    aW = hUtils.find_object_width(at_path)
                else:
                    aL = 0
                    aW = 0
            else:
                aL = 0
                aW = 0

            with open(os.path.join(save_folder, 'data.txt'), 'w') as f:
                f.write(
                    f've_area:{ve_area}\n'
                    f'at_area:{at_area}\n'
                    f've_length:{round(vL,1)}\n'
                    f've_width:{round(vW,1)}\n'
                    f'at_length:{round(aL,1)}\n'
                    f'at_width:{round(aW,1)}')
                f.close()
        else:
            break
    cap.release()

    testData = []
    flag = 1
    for i,filename in enumerate(os.listdir(out_folder)):
        file_path = os.path.join(out_folder,f'{i}')
        data_path = os.path.join(file_path,'data.txt')
        if(os.access(data_path,os.F_OK)):
            dic = {'clip':f'{i}'}
            f = open(data_path)
            for line in f.readlines():
               dic[f'{line.split(":")[0]}'] = float(line.split(":")[1])
            testData.append(dic)
        else:
            continue
    hUtils.op_toExcel(testData, fileName)

    hUtils.data_clean(fileName)

    hUtils.data_scale(fileName,scale)

    hUtils.data_compute(fileName)

# img_folder = r'D:\environmentalPaper\VIDEO\IMAGE'
# result_folder = r'D:\environmentalPaper\VIDEO\RESULT'
# os.makedirs(result_folder, exist_ok=True)
#
# for i,filename in enumerate(os.listdir(img_folder)):
#     # 视频所在路径
#     img_path = os.path.join(img_folder,filename)
#
#     img = cv2.imread(img_path)
#
#     # imgsz根据原图片尺寸调整
#     AT_results = AT_model.predict(source=img_path)
#     VE_results = VE_model.predict(source=img_path)
#
#     if len(AT_results[0].boxes) == 0 or len(VE_results[0].boxes) == 0:
#         # 预测结果输出文件夹
#         out_path = os.path.join(result_folder,f'{os.path.basename(filename).split(".AVI")[0]}'+str(i))
#         os.makedirs(out_path, exist_ok=True)
#         cv2.imwrite(os.path.join(out_path,"PHOTO.png"),img)
#         cv2.imwrite(os.path.join(out_path,"AT.png"), AT_results[0].plot(boxes=True))
#         cv2.imwrite(os.path.join(out_path,"VE.png"), VE_results[0].plot(boxes=True))