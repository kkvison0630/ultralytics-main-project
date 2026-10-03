import cv2
import numpy as np
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os
import math

def find_contours(binary_image):
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        longest_contour = max(contours, key=lambda contour: cv2.arcLength(contour, True))
        return longest_contour
    else:
        raise ValueError("未检测到任何轮廓")

def draw_line(image, start_point, end_point):
    line_image = np.zeros_like(image)
    cv2.line(line_image, start_point, end_point, 255, 1)
    return line_image

def calculate_area(binary_image, contour, start_point, end_point):
    line_image = draw_line(binary_image, start_point, end_point)
    combined_image = cv2.bitwise_or(binary_image, line_image)
    combined_contours, _ = cv2.findContours(combined_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area = 0
    for cnt in combined_contours:
        area += cv2.contourArea(cnt)
    area -= cv2.contourArea(np.array([start_point, end_point]))
    return area, combined_image

def scale_image(image, start_point, end_point, target_length):
    current_length = np.linalg.norm(np.array(start_point) - np.array(end_point))
    scale_factor = target_length / current_length
    scaled_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    scaled_start_point = tuple((np.array(start_point) * scale_factor).astype(int))
    scaled_end_point = tuple((np.array(end_point) * scale_factor).astype(int))
    return scaled_image, scaled_start_point, scaled_end_point

def area(image_path):
    binary_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary_image = cv2.threshold(binary_image, 127, 255, cv2.THRESH_BINARY)
    points = extract_skeleton_points(binary_image)
    if len(points) < 3:
        raise ValueError("骨架点数不足，无法进行曲线拟合")
    x, y = points[:, 0], points[:, 1]
    start_point = (x[0], y[0])
    end_point = (x[-1], y[-1])
    target_length = 300
    scaled_image, scaled_start_point, scaled_end_point = scale_image(binary_image, start_point, end_point, target_length)
    contour = find_contours(scaled_image)
    area, combined_image = calculate_area(scaled_image, contour, scaled_start_point, scaled_end_point)
    return area

def rotate_image_to_horizontal(start_point, end_point):
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    angle = math.degrees(math.atan2(dy, dx))
    rotation_angle = -angle

    return rotation_angle

def find_enclosing_circle(image_path):

    image = cv2.imread(image_path)
    if image is None:
        return (320,320)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_radius = 0
    best_circle = None
    for contour in contours:
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius > max_radius:
            max_radius = radius
            best_circle = (int(x), int(y), int(radius))

    if best_circle is None:
        raise ValueError("没有找到外接圆")

    center_x, center_y, radius = best_circle

    return center_x, center_y

def extract_skeleton_points(binary_image):
    points = np.column_stack(np.where(binary_image.transpose() > 0))
    return points

def smooth_curve(x, y, smooth_factor=0.1):
    smoothed_points = []
    for i in range(len(x)):
        window_start = max(0, i - int(smooth_factor * len(x)))
        window_end = min(len(x), i + int(smooth_factor * len(x)))
        smoothed_x = np.mean(x[window_start:window_end])
        smoothed_y = np.mean(y[window_start:window_end])
        smoothed_points.append((smoothed_x, smoothed_y))
    smoothed_points = np.array(smoothed_points)
    return smoothed_points[:, 0], smoothed_points[:, 1]

def calculate_curvature(x, y):
    dx = np.gradient(x)
    dy = np.gradient(y)
    d2x = np.gradient(dx)
    d2y = np.gradient(dy)
    curvature = np.abs(d2x * dy - dx * d2y) / (dx**2 + dy**2)**1.5

    ds = np.sqrt(dx ** 2 + dy ** 2)

    curvature_squared = curvature ** 2

    bending_energy = np.sum(curvature_squared * ds)

    return curvature, bending_energy

def find_max_curvature_point(curvature, x_fit, y_fit):
    max_curvature_index = np.argmax(curvature)
    max_curvature_x = x_fit[max_curvature_index]
    max_curvature_y = y_fit[max_curvature_index]
    return max_curvature_x, max_curvature_y, max_curvature_index

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

def rotate_image(image, angle):
    center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return rotated_image,rot_mat

def find_and_apply_circle(image1_path, image2_path):

    image2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)
    _, binary_image2 = cv2.threshold(image2, 127, 255, cv2.THRESH_BINARY)

    if os.path.isfile(image1_path):
        image1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
        _, binary_image1 = cv2.threshold(image1, 127, 255, cv2.THRESH_BINARY)

    else:
        return binary_image2,False

    contours, _ = cv2.findContours(binary_image1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(largest_contour)
        center = (int(x), int(y))
        radius = int(radius) * 3
        mask = np.zeros_like(binary_image2)
        cv2.circle(mask, center, radius, 255, -1)
        binary_image2[mask == 255] = 0

        return binary_image2,True

    else:
        return binary_image2,False

def apply_rotation_to_point(point, rot_mat):
    point = np.append(point, 1)
    rotated_point = np.dot(rot_mat, point)
    return rotated_point[:2]

def process_image(image_path,external_point):
    skel_legth = calculate_skeleton_length(image_path)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("图像读取失败，请检查路径")

    points = extract_skeleton_points(image)
    if len(points) < 3:
        raise ValueError("骨架点数不足，无法进行曲线拟合")

    x, y = points[:, 0], points[:, 1]

    area_bia = area(image_path)

    angle = rotate_image_to_horizontal((x[0],y[0]),(x[-1],y[-1]))

    parent_dir = os.path.dirname(image_path)
    skel_image,flag = find_and_apply_circle(os.path.join(parent_dir,'head.png'),image_path)
    image, rot_mat = rotate_image(skel_image, -angle)
    points = extract_skeleton_points(image)
    if len(points) < 3:
        raise ValueError("旋转后的骨架点数不足，无法进行曲线拟合")
    x, y = points[:, 0], points[:, 1]

    xy = np.column_stack((x, y))
    xy = np.unique(xy, axis=0)
    x, y = xy[:, 0], xy[:, 1]

    x_smooth, y_smooth = smooth_curve(x, y, smooth_factor=0.1)
    x_smooth = np.concatenate(([x[0]], x_smooth, [x[-1]]))
    y_smooth = np.concatenate(([y[0]], y_smooth, [y[-1]]))

    tck, u = splprep([x_smooth, y_smooth], s=1, k=1)
    unew = np.linspace(0, 1, 100000)
    x_fit, y_fit = splev(unew, tck)

    external_point = apply_rotation_to_point(external_point,rot_mat)
    start_point = np.array([x_fit[0], y_fit[0]])
    end_point = np.array([x_fit[-1], y_fit[-1]])

    start_to_end = np.linalg.norm(start_point - end_point)
    dist_to_start = np.linalg.norm(external_point - start_point)
    dist_to_end = np.linalg.norm(external_point - end_point)

    if dist_to_end < dist_to_start:
        x_fit = x_fit[::-1]
        y_fit = y_fit[::-1]

    curvature,bending_energy = calculate_curvature(x_fit, y_fit)

    max_curvature_x, max_curvature_y, max_curvature_index = find_max_curvature_point(curvature, x_fit, y_fit)
    max_curvature = curvature[max_curvature_index]
    position_along_curve = max_curvature_index / (len(curvature) - 1)  # 归一化到[0, 1]范围内

    # plt.figure(figsize=(10, 10))
    # plt.imshow(image, cmap='gray')
    # plt.plot(x, y, 'o', label='Original Points')
    # plt.plot(x_fit, y_fit, '-', label='Fitted Curve')
    # plt.plot(max_curvature_x, max_curvature_y, 'ro', label='Max Curvature Point')
    # plt.legend()
    # plt.title('Curve and Curvature')
    # # plt.gca().invert_yaxis()
    # plt.show()

    return max_curvature,bending_energy,skel_legth / start_to_end,area_bia,position_along_curve

# image_path = r'C:\result_of_zebrafish_curve\results_excurve\925zebra B112_G03_w1.tif\skel.png'
# file_path = os.path.dirname(image_path)
# head_path = os.path.join(file_path, 'head.png')
# eye_path = os.path.join(file_path, 'eye.png')
# yolk_path = os.path.join(file_path, 'yolk.png')
# heart_path = os.path.join(file_path, 'heart.png')
# if os.path.exists(head_path) and os.path.isfile(head_path):
#     external_point = find_enclosing_circle(head_path)
# elif os.path.exists(eye_path) and os.path.isfile(eye_path):
#     external_point = find_enclosing_circle(eye_path)
# elif os.path.exists(heart_path) and os.path.isfile(heart_path):
#     external_point = find_enclosing_circle(heart_path)
# elif os.path.exists(yolk_path) and os.path.isfile(yolk_path):
#     external_point = find_enclosing_circle(yolk_path)
# else:
#     external_point = (320, 320)
# max_curvature,bend,SL,area_bia,position_along_curve, = process_image(image_path,external_point)
# print(f'Max Curvature: {max_curvature}\tBending energy:{bend}\tS/L:{SL}\tArea bias:{area_bia}\tPosition:{position_along_curve}')

def curve_data(file_path,curve_data_list):
    if os.path.isdir(file_path):
        skel_path = os.path.join(file_path,'skel.png')
        head_path = os.path.join(file_path,'head.png')
        eye_path = os.path.join(file_path,'eye.png')
        yolk_path = os.path.join(file_path,'yolk.png')
        heart_path = os.path.join(file_path,'heart.png')
        if os.path.exists(head_path) and os.path.isfile(head_path):
            external_point = find_enclosing_circle(head_path)
        elif os.path.exists(eye_path) and os.path.isfile(eye_path):
            external_point = find_enclosing_circle(eye_path)
        elif os.path.exists(heart_path) and os.path.isfile(heart_path):
            external_point = find_enclosing_circle(heart_path)
        elif os.path.exists(yolk_path) and os.path.isfile(yolk_path):
            external_point = find_enclosing_circle(yolk_path)
        else:
            external_point = (320,320)
        max_curvature,bend,SL,area_bia,position_along_curve = process_image(skel_path,external_point)
        curve_data_list.append(max_curvature)
        curve_data_list.append(bend)
        curve_data_list.append(SL)
        curve_data_list.append(area_bia)
        curve_data_list.append(position_along_curve)

        return curve_data_list

# data_list = []
# result_folder = r'C:\ultralytics-main\results_excurve'
# for i,filename in enumerate(os.listdir(result_folder)):
#     file_path = os.path.join(result_folder,filename)
#     list = []
#     list = curve_data(file_path,list)
#     data_list.append(list)
# # print(data_list[0])
# txt_path = r'C:\ultralytics-main\excurve_1.txt'
# for data in data_list:
#     with open(txt_path,'a') as file:
#         file.write(f'{data}\n')