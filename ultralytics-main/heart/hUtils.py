import cv2
import numpy as np
import openpyxl as op
import math
import openpyxl

def find_object_length(mask_path):
    image = cv2.imread(mask_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_index = 0
    max_area = 0
    for i,cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_index = i

    (x, y), radius = cv2.minEnclosingCircle(max(contours, key=cv2.contourArea))
    center = (int(x), int(y))
    radius = int(radius)

    # 找到外接圆上的所有点
    points_on_circle = np.array([[int(center[0] + radius * np.cos(theta)),
                                  int(center[1] + radius * np.sin(theta))] for theta in np.arange(0, 2 * np.pi, 0.01)])

    # 找到物体轮廓上的点
    points_on_contour = cv2.approxPolyDP(contours[max_index], 0.02 * cv2.arcLength(contours[max_index], True), True)

    # 找到物体与外接圆的两个交点
    max_distance = 0
    farthest_point1 = None
    farthest_point2 = None

    for point_contour in points_on_contour:
        for point_circle in points_on_circle:
            distance = np.sqrt(
                (point_circle[0] - point_contour[0][0]) ** 2 + (point_circle[1] - point_contour[0][1]) ** 2)
            if distance > max_distance:
                max_distance = distance
                farthest_point1 = tuple(point_contour[0])
                farthest_point2 = tuple(point_circle)

    return max_distance


def find_object_width(img_path):
    image = cv2.imread(img_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    W = 0
    for cont in contours:
        # 对每个轮廓点求最小外接矩形
        rect = cv2.minAreaRect(cont)
        # cv2.boxPoints可以将轮廓点转换为四个角点坐标
        box = cv2.boxPoints(rect)
        # 这一步不影响后面的画图，但是可以保证四个角点坐标为顺时针
        startidx = box.sum(axis=1).argmin()
        box = np.roll(box, 4 - startidx, 0)
        # 找出宽度
        L_1 = math.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2)
        L_2 = math.sqrt((box[0][0] - box[3][0]) ** 2 + (box[0][1] - box[3][1]) ** 2)
        if (L_1 > L_2):
            W = L_2
        else:
            W = L_1
    return W

def op_toExcel(data, fileName):  # openpyxl库储存数据到excel
    wb = op.Workbook()  # 创建工作簿对象
    ws = wb['Sheet']  # 创建子表
    ws.append(['clip', 've_area', 'at_area','ve_length','ve_width','at_length','at_width'])  # 添加表头
    for i in range(len(data)):
        d = data[i]["clip"], data[i]["ve_area"], data[i]["at_area"],data[i]["ve_length"],data[i]["ve_width"],data[i]["at_length"],data[i]["at_width"]
        ws.append(d)  # 每次写入一行
    wb.save(fileName)


def data_clean(exccel_path):
    file = exccel_path

    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active

    delete_list = []

    # 设定阈值
    threshold = 10

    for row_idx in range(2, sheet.max_row + 1):
        # 获取特定单元格的值
        cell_value1 = sheet.cell(row=row_idx, column=4).value
        cell_value2 = sheet.cell(row=row_idx, column=5).value
        cell_value3 = sheet.cell(row=row_idx, column=6).value
        cell_value4 = sheet.cell(row=row_idx, column=7).value

        # 判断是否小于阈值
        if cell_value1 < threshold or cell_value2 < threshold or cell_value3 < threshold or cell_value4 < threshold:
            delete_list.append(row_idx)

    delete_list = delete_list[::-1]

    for index in delete_list:
        sheet.delete_rows(index, amount=1)

    # 保存修改
    workbook.save(file)


def data_scale(excel_path, scale):
    file = excel_path
    # 打开 Excel 文件
    workbook = openpyxl.load_workbook(file)

    # 选择第一个工作表
    sheet = workbook.active

    for row in range(2, sheet.max_row + 1):
        # 读取两列的值
        value1 = sheet.cell(row=row, column=2).value
        value2 = sheet.cell(row=row, column=3).value
        value3 = sheet.cell(row=row, column=4).value
        value4 = sheet.cell(row=row, column=5).value
        value5 = sheet.cell(row=row, column=6).value
        value6 = sheet.cell(row=row, column=7).value

        # 计算乘积
        update_value1 = value1 * pow(scale, 2)
        update_value2 = value2 * pow(scale, 2)
        update_value3 = value3 * scale
        update_value4 = value4 * scale
        update_value5 = value5 * scale
        update_value6 = value6 * scale

        # 将结果存储到第七列，G列
        sheet.cell(row=row, column=2).value = update_value1
        sheet.cell(row=row, column=3).value = update_value2
        sheet.cell(row=row, column=4).value = update_value3
        sheet.cell(row=row, column=5).value = update_value4
        sheet.cell(row=row, column=6).value = update_value5
        sheet.cell(row=row, column=7).value = update_value6

    # 保存修改
    workbook.save(file)


def data_compute(excel_path):
    file = excel_path
    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active

    sheet.cell(row=1, column=2).value = 've_area'
    sheet.cell(row=1, column=3).value = 'at_area'
    sheet.cell(row=1, column=4).value = 've_length'
    sheet.cell(row=1, column=5).value = 've_width'
    sheet.cell(row=1, column=6).value = 'at_length'
    sheet.cell(row=1, column=7).value = 'at_width'
    sheet.cell(row=1, column=9).value = 've_volume'
    sheet.cell(row=1, column=10).value = 'EDV'
    sheet.cell(row=1, column=11).value = 'ESV'
    sheet.cell(row=1, column=12).value = 'SV'
    sheet.cell(row=1, column=13).value = 'FAC'
    sheet.cell(row=1, column=14).value = 'EF'
    sheet.cell(row=1, column=15).value = 'FS'
    sheet.cell(row=1, column=16).value = 'at_volume'

    # 循环遍历每一行，计算乘积并存储到另外一列
    for row in range(2, sheet.max_row + 1):
        # 读取两列的值
        value1 = sheet.cell(row=row, column=4).value
        value2 = sheet.cell(row=row, column=5).value
        value3 = sheet.cell(row=row, column=6).value
        value4 = sheet.cell(row=row, column=7).value

        # 计算乘积
        ve_volume = value1 * value2 * value2 * math.pi / 6
        at_volume = value3 * value4 * value4 * math.pi / 6

        # 将结果存储到第七列，G列
        sheet.cell(row=row, column=9).value = ve_volume
        sheet.cell(row=row, column=16).value = at_volume

    max_V = 0
    min_V = 999999999
    max_index = 0
    min_index = 0

    for row in range(2, sheet.max_row + 1):
        volume = sheet.cell(row=row, column=9).value
        if (volume > max_V):
            max_V = volume
            max_index = row
        if (volume < min_V):
            min_V = volume
            min_index = row

    sheet.cell(row=2, column=10).value = max_V
    sheet.cell(row=2, column=11).value = min_V

    SV = max_V - min_V
    EDA = sheet.cell(row=max_index, column=2).value
    ESA = sheet.cell(row=min_index, column=2).value
    FAC = (EDA - ESA) / EDA * 100
    EF = (max_V - min_V) / max_V * 100
    Dd = sheet.cell(row=max_index, column=5).value
    Ds = sheet.cell(row=min_index, column=5).value
    FS = (Dd - Ds) / Dd * 100

    sheet.cell(row=2, column=12).value = abs(SV)
    sheet.cell(row=2, column=13).value = abs(FAC)
    sheet.cell(row=2, column=14).value = abs(EF)
    sheet.cell(row=2, column=15).value = abs(FS)

    # 保存修改
    workbook.save(file)