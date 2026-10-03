#
import cv2
import numpy as np
import imgaug.augmenters as iaa
import matplotlib.pyplot as plt
from matplotlib import font_manager

plt.rcParams['font.sans-serif'] = ['Times New Roman']  # 使用黑体字体
plt.rcParams['font.size'] = 20
plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# 读取图像
image = cv2.imread(r'C:\Users\JP_Wang\Desktop\heart\B-1-B.AVI6.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 定义各个增强方法
augmenters = [
    iaa.SaltAndPepper(0.1),
    iaa.AdditiveGaussianNoise(scale=10),
    iaa.GaussianBlur(sigma=(0.0, 5.0)),
    iaa.Rotate((-45, 45)),
    iaa.TranslateX(px=(-20, 20)),
    iaa.Affine(scale={"x": (0.5, 1.5), "y": (0.5, 1.5)}),
    iaa.Fliplr(0.7),
    iaa.Flipud(0.7),
    iaa.GammaContrast((0.5, 2.0)),
    iaa.LinearContrast((0.8, 1.2), per_channel=0.5),
    iaa.WithBrightnessChannels(iaa.Add((-50, 50))),
    iaa.AddToHueAndSaturation((-30, 30)),
    iaa.Sometimes(0.75, iaa.Snowflakes())
]

# 对应的增强方法名称
augmenter_names = [
    "Salt & Pepper Noise",
    "Gaussian Noise",
    "Gaussian Blur",
    "Rotate",
    "Translation",
    "Scaling",
    "Horizontal Flip",
    "Vertical Flip",
    "Gamma Contrast",
    "Linear Contrast",
    "Brightness Adjustment",
    "Hue and Saturation Transformation",
    "Snowflake Effect"

    # "椒盐噪声",
    # "高斯噪声",
    # "高斯模糊",
    # "旋转",
    # "平移",
    # "缩放",
    # "水平翻转",
    # "垂直翻转",
    # "伽马对比度调整",
    # "线性对比度调整",
    # "亮度调整",
    # "色调饱和度变换",
    # "雪花效果"
]

# 生成增强后的图像
images_aug = [aug(images=[image])[0] for aug in augmenters]

# 显示原始图像和增强后的图像
plt.figure(figsize=(20, 15))

# 显示原始图像
plt.subplot(4, 4, 1)
plt.imshow(image)
plt.title("Original Image")
plt.axis('off')

# 显示增强后的图像
for i, (img_aug, name) in enumerate(zip(images_aug, augmenter_names)):
    plt.subplot(4, 4, i+2)
    plt.imshow(img_aug)
    plt.title(name)
    plt.axis('off')

plt.tight_layout()
plt.show()
