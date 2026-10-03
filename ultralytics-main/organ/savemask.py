import os
from ultralytics import YOLO
import cv2
import numpy as np
import openpyxl as op
import pickle
import curve_test


def curve_predict(pkl, list):
    with open(pkl, 'rb') as f:
        loaded_clf = pickle.load(f)

    new_data = np.array([list[0:4]])
    new_predictions = loaded_clf.predict(new_data)

    if new_predictions != 0:
        if list[-1] >= 0.7:
            new_predictions = 3

    return int(new_predictions)

def largest_component(image):
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    largest_component = np.zeros_like(binary)
    largest_component[labels == largest_label] = 255

    return largest_component

def op_toExcel(data, fileName):
    wb = op.Workbook()
    ws = wb['Sheet']
    ws.append(['filename', 'head_area', 'eye_area','heart_area','yolk_area','length','curvature'])
    for i in range(len(data)):
        d = data[i]["filename"], data[i]["head_area "], data[i]["eye_area "],data[i]["heart_area "],data[i]["yolk_area "],data[i]["length "],data[i]["curvature "]
        ws.append(d)
    wb.save(fileName)

def calculate_skeleton_length(skel_path):
    binary_image = cv2.imread(skel_path, cv2.IMREAD_GRAYSCALE)
    _, binary_image = cv2.threshold(binary_image, 0, 255, cv2.THRESH_BINARY)

    contours = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    if contours:
        longest_contour = max(contours, key=lambda contour: cv2.arcLength(contour, True))

        perimeter = cv2.arcLength(longest_contour, True)

        length = perimeter / 2
        return length
    else:
        raise ValueError("未检测到任何线段")

scale = 2048 / 1280 * 3.414 #2048-原始图像分辨率   3.414-像素比例
scale_body = 2048 / 640 * 3.414

def predict_and_save_masks(image_path, output_dir):
    model1 = YOLO(r"..\weights_new\organ.pt")  #器官
    model2 = YOLO(r"..\weights_new\body.pt")  #鱼身

    pkl = r'..\weights_new\curve_classifier.pkl'  #曲率

    class_dict1 = {
        0: 'head',
        1: 'eye',
        2: 'heart',
        3: 'yolk'
    }

    class_dict2 = {
        0: 'body'
    }

    class_dict3 = {
        -1: 'NULL',
        0: 'straight',
        1: 'curve',
        2: 'extreme curvature',
        3: 'tail bend'
    }

    results1 = model1.predict(source=image_path)
    results2 = model2.predict(source=image_path)

    for result in results1:
        if result.masks is not None and len(result.masks) > 0 :
            mask_data = result.masks.data
            area_list = [0,0,0,0]
            for index,mask in enumerate(mask_data):
                mask=mask.cpu().numpy()*255
                cv2.imwrite(os.path.join(output_dir,f'{class_dict1[int(result.boxes.cls[index].cpu().numpy())]}.png'),mask)
                mask = cv2.imread(os.path.join(output_dir,f'{class_dict1[int(result.boxes.cls[index].cpu().numpy())]}.png'))
                img = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)[1]
                area = 0
                contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
                for j in range(len(contours)):
                    area += cv2.contourArea(contours[j])
                area_list[int(result.boxes.cls[index].cpu().numpy())]=area
            head_area = area_list[0] + area_list[1]
            eye_area = area_list[1]
            heart_area = area_list[2]
            yolk_area = area_list[3]

        else:
            head_area = 0.0
            eye_area = 0.0
            heart_area = 0.0
            yolk_area = 0.0


    for result in results2:
        if result.masks is not None and len(result.masks) > 0 :
            mask_data = result.masks.data
            scores = result.boxes.conf.cpu().numpy()
            mask=mask_data[np.argmax(scores)].cpu().numpy()*255
            cv2.imwrite(os.path.join(output_dir,f'{class_dict2[int(result.boxes.cls[np.argmax(scores)].cpu().numpy())]}.png'),mask)

            body_image = cv2.imread(os.path.join(output_dir,'body.png'), cv2.IMREAD_GRAYSCALE)

            _, binary_image = cv2.threshold(body_image, 0, 255, cv2.THRESH_BINARY)
            skel = cv2.ximgproc.thinning(binary_image, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
            skel = largest_component(skel)
            cv2.imwrite(os.path.join(output_dir,'skel.png'), skel)

            body_length = calculate_skeleton_length(os.path.join(output_dir,'skel.png'))

            curve_data_list = []

            curve_data_list = curve_test.curve_data(output_dir, curve_data_list)

            curve_prediction = curve_predict(pkl, curve_data_list)

        else:
            body_length = 0.0
            curve_prediction = -1

    with open(os.path.join(output_dir, 'data.txt'), 'w') as f:
        f.write(f'head_area : {head_area * scale * scale}\neye_area : {eye_area * scale * scale}\nheart_area : {heart_area * scale * scale}\nyolk_area : {yolk_area * scale * scale}\nlength : {body_length * scale_body}\ncurvature : {class_dict3[curve_prediction]}\n')
        f.close()

img_folder = r'H:\PyCharm\tupian' #图片所在文件夹
output_dir = r'H:\PyCharm\tupian_test' #结果输出文件夹
for i,filename in enumerate(os.listdir(img_folder)):
    output_dir_son = os.path.join(output_dir,filename)
    os.makedirs(output_dir_son,exist_ok=True)
    image_path = os.path.join(img_folder,filename)
    predict_and_save_masks(image_path,output_dir_son)


testData = []
for filename in os.listdir(output_dir):
    file_path = os.path.join(output_dir,filename)
    data_path = os.path.join(file_path,'data.txt')
    if(os.access(data_path,os.F_OK)):
        dic = {'filename':f'{filename.split(".")[0]}'}
        f = open(data_path)
        for line in f.readlines():
           dic[f'{line.split(":")[0]}'] = line.split(":")[1]
        testData.append(dic)
    else:
        dic = {'filename':f'{filename.split(".")[0]}','head_area ':0.0,'eye_area ':0.0,'heart_area ':0.0,'yolk_area ':0.0,'length ':0.0, 'curvature ':'NULL'}
        testData.append(dic)
        continue

op_toExcel(testData, os.path.join(output_dir,'data.xlsx'))