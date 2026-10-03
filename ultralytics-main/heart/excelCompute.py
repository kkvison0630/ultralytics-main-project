import openpyxl
import math
import os

# folder_path = r'C:\Users\JP_Wang\Documents\WeChat Files\wxid_xu6r6np3v15h22\FileStorage\File\2024-04\心脏'
# for filename in os.listdir(folder_path):
#     excel_folder_path = os.path.join(folder_path,filename)
#     for excel_folder in os.listdir(excel_folder_path):
#         excel_path = os.path.join(excel_folder_path,excel_folder)
#         for excel in os.listdir(excel_path):

def data_compute(excel_path):
    file = excel_path
    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active

    sheet.cell(row=1, column=2).value = 'at_area'
    sheet.cell(row=1, column=3).value = 've_area'
    sheet.cell(row=1, column=4).value = 'at_length'
    sheet.cell(row=1, column=5).value = 'at_width'
    sheet.cell(row=1, column=6).value = 've_length'
    sheet.cell(row=1, column=7).value = 've_width'
    sheet.cell(row=1, column=9).value = 'volume'
    sheet.cell(row=1, column=10).value = 'EDV'
    sheet.cell(row=1, column=11).value = 'ESV'
    sheet.cell(row=1, column=12).value = 'SV'
    sheet.cell(row=1, column=13).value = 'FAC'
    sheet.cell(row=1, column=14).value = 'EF'
    sheet.cell(row=1, column=15).value = 'FS'

    # 循环遍历每一行，计算乘积并存储到另外一列
    for row in range(2, sheet.max_row + 1):
        # 读取两列的值
        value1 = sheet.cell(row=row, column=6).value
        value2 = sheet.cell(row=row, column=7).value

        # 计算乘积
        product = value1 * value2 * value2 * math.pi / 6

        # 将结果存储到第七列，G列
        sheet.cell(row=row, column=9).value = product

    max_V = 0
    min_V = 999999999
    max_index = 0
    min_index = 0

    for row in range(2, sheet.max_row + 1):
        volume = sheet.cell(row=row, column=9).value
        if(volume > max_V):
            max_V = volume
            max_index = row
        if(volume < min_V):
            min_V = volume
            min_index = row

    sheet.cell(row=2, column=10).value = max_V
    sheet.cell(row=2, column=11).value = min_V

    SV = max_V - min_V
    EDA = sheet.cell(row=max_index, column=3).value
    ESA = sheet.cell(row=min_index, column=3).value
    FAC = (EDA - ESA) / EDA * 100
    EF = (max_V - min_V) / max_V * 100
    Dd = sheet.cell(row=max_index, column=7).value
    Ds = sheet.cell(row=min_index, column=7).value
    FS = (Dd - Ds) / Dd * 100

    sheet.cell(row=2, column=12).value = abs(SV)
    sheet.cell(row=2, column=13).value = abs(FAC)
    sheet.cell(row=2, column=14).value = abs(EF)
    sheet.cell(row=2, column=15).value = abs(FS)

    # 保存修改
    workbook.save(file)