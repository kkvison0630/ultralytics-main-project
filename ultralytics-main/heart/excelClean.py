import openpyxl
import os

# folder_path = r'C:\Users\JP_Wang\Documents\WeChat Files\wxid_xu6r6np3v15h22\FileStorage\File\2024-04\心脏'
# for filename in os.listdir(folder_path):
#     excel_folder_path = os.path.join(folder_path,filename)
#     for excel_folder in os.listdir(excel_folder_path):
#         excel_path = os.path.join(excel_folder_path,excel_folder)
#         for excel in os.listdir(excel_path):

def data_clean(exccel_path):
    file = r"C:\ultralytics-main\test0402.xlsx"

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
        if cell_value1 < threshold or cell_value2 < threshold or cell_value3 < threshold or cell_value4 <threshold:
            delete_list.append(row_idx)

    delete_list = delete_list[::-1]

    for index in delete_list:
        sheet.delete_rows(index,amount=1)

    # 保存修改
    workbook.save(file)
