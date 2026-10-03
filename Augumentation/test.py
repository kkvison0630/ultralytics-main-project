import imageio
import imgaug as ia
import numpy as np
from imgaug.augmentables.polys import Polygon, PolygonsOnImage
import imgaug.augmenters as iaa

class LabelJson(object):
    def __init__(self, abs_path=None) -> None:
        super().__init__()
        self.abs_path = abs_path
        self.read()

    def read(self):
        with open(self.abs_path, 'r', encoding='utf-8') as f:
            lj = json.load(f)
        self.wh = [lj.get('imageWidth'), lj.get('imageHeight')]
        shapes = lj.get('shapes')
        self.cls = [i.get('label') for i in shapes]  # '1305' if i.get('label') == '14' else
        points = [i.get('points') for i in shapes]
        points = [np.array(i, dtype=np.int32).reshape((-1, 2)) for i in points]
        self.loc = points
        self.box = [[j[:, 0].min(), j[:, 1].min(), j[:, 0].max(), j[:, 1].max()] for j in points]
        self.img_name = lj.get('imagePath')
        self.is_pos = bool(self.cls)
        return self

import base64, os
from PIL import Image
import io
import json
import cv2
def base64encode_img(src_image):
    # src_image = Image.open(image_path)
    src_image = Image.fromarray(cv2.cvtColor(src_image, cv2.COLOR_BGR2RGB))
    output_buffer = io.BytesIO()
    src_image.save(output_buffer, format='JPEG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode('utf-8')
    return base64_str

def savejson(points_list, clses_list, img_tmp, filename, save_dir):
    A = dict()
    listbigoption = []
    for cls, points in zip(clses_list, points_list):
        listobject = dict()

        listobject['points'] = points
        listobject['line_color'] = 'null'
        listobject['label'] = cls

        listobject['fill_color'] = 'null'
        listbigoption.append(listobject)

    A['imageData'] = base64encode_img(img_tmp)
    A['imagePath'] = filename
    A['shapes'] = listbigoption
    A['flags'] = {}

    suffix = os.path.splitext(filename)[-1]
    with open(save_dir + "/" + filename.replace(suffix, ".json"), 'w', encoding='utf-8') as f:
        json.dump(A, f, indent=2, ensure_ascii=False)


def saveJsonImg_main(image_aug, psoi_aug, cls_list, img_path, num, save_dir):
    nw, nh, _ = image_aug.shape

    points_list = []
    for pos in psoi_aug:
        points = [list(xy.astype(np.float64)) for xy in pos]
        for p in points:
            if p[0] < 0:
                p[0] = 0
            elif p[0] > nh:
                p[0] = nh
            if p[1] < 0:
                p[1] = 0
            elif p[1] > nw:
                p[1] = nw
        points_list.append(points)

    image_augRGB = cv2.cvtColor(image_aug, cv2.COLOR_BGR2RGB)
    savejson(points_list, cls_list, image_augRGB, str(num)+'_'+os.path.basename(img_path), save_dir)
    # ia.imshow(psoi_aug.draw_on_image(image_aug, alpha_face=0.2, size_points=7))
    cv2.imwrite(os.path.join(save_dir, str(num)+'_'+os.path.basename(img_path)), image_augRGB)


ia.seed(2)
aug = iaa.Sequential([
    iaa.OneOf([
        iaa.SaltAndPepper(0.01),
        iaa.AdditiveGaussianNoise(scale=5),
        iaa.GaussianBlur(sigma=(0.0, 3.0)),
        ]),
    iaa.OneOf([
        iaa.Affine(rotate=(-20, 20), translate_percent=(-0.2, 0.2), scale=(0.8, 1.2),
                   mode=["constant", "edge"], cval=0),  # 放射变换
        iaa.Affine(scale={"x": (0.5, 1.5), "y": (0.5, 1.5)}),
        iaa.Affine(translate_px={"x": (-20, 20), "y": (-20, 20)}),
        iaa.TranslateX(px=(-20, 20)),
        iaa.Rotate((-45, 45))
        ]),
    iaa.OneOf([
        iaa.Fliplr(0.7),    # 水平翻转
        iaa.Flipud(0.7),    # 上下翻转
        ]),
    iaa.OneOf([
        iaa.GammaContrast((0.5, 2.0)),
        iaa.LinearContrast((0.8, 1.2), per_channel=0.5),
        iaa.WithBrightnessChannels(iaa.Add((-50, 50))),     # Augmenter to apply child augmenters to brightness-related image channels.
        iaa.AddToHueAndSaturation((-20, 20)),   # 通过随机值增加或减少色调和饱和度。
        ]),

    iaa.Sometimes(0.75, iaa.Snowflakes())
])

def main():
    img_dir = r"C:\Users\JP_Wang\Desktop\heart\IMAGE"
    json_dir = r'C:\Users\JP_Wang\Desktop\heart\JSON_VE'
    save_dir = r'C:\Users\JP_Wang\Desktop\heart\IMAGE_VE'

    for file in os.listdir(img_dir):
        img_path = os.path.join(img_dir, file)
        json_path = os.path.join(json_dir, file.replace('.jpg', '.json'))

        # read image and get json info
        image = imageio.imread(img_path)
        json_info = LabelJson(json_path)

        #  let's convert our polygons to an PolygonsOnImage instance:
        psoi = ia.PolygonsOnImage([Polygon(point) for point in json_info.loc],
                                  shape=image.shape)

        # one labelme image aug to 5 image
        for num in range(5):
            # aug
            image_aug, psoi_aug = aug(image=image, polygons=psoi)

            # save json and image
            saveJsonImg_main(image_aug, psoi_aug, json_info.cls, img_path, num, save_dir)


if __name__ == '__main__':
    main()
