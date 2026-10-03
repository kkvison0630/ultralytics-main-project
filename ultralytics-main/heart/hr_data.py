import os
from hrUtils import data_compute

excel_folder = r'H:\PyCharm\excel'

for i,file in enumerate(os.listdir(excel_folder)):
    file_path = os.path.join(excel_folder,file)
    print(file)
    data_compute(file_path)