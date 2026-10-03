import openpyxl
import math
import os

# folder_path = r'C:\Users\JP_Wang\Documents\WeChat Files\wxid_xu6r6np3v15h22\FileStorage\File\2024-04\心脏'
# for filename in os.listdir(folder_path):
#     excel_folder_path = os.path.join(folder_path,filename)
#     for excel_folder in os.listdir(excel_folder_path):
#         excel_path = os.path.join(excel_folder_path,excel_folder)
#         for excel in os.listdir(excel_path):

def data_scale(excel_path,scale):
    file = os.path.join(excel_path)
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
        update_value1 = value1 * pow(scale,2)
        update_value2 = value2 * pow(scale,2)
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