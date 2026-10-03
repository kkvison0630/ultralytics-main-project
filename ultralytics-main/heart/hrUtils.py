import openpyxl

def time_to_milliseconds(t):
    return (t.hour * 3600 + t.minute * 60 + t.second) * 1000 + t.microsecond // 1000

def sub_times_in_milliseconds(time1, time2):
    ms1 = time_to_milliseconds(time1)
    ms2 = time_to_milliseconds(time2)

    total_milliseconds = ms2 - ms1
    return total_milliseconds



def find_column_by_content(file_path,target_content):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    for cell in sheet[1]:
        if cell.value == target_content:
            return cell.column

def findHRTB(path):
    workbook = openpyxl.load_workbook(path)

    sheet = workbook.active

    top_dict_array = []
    bottom_dict_array = []
    top_flag = True

    rate_column = find_column_by_content(path,'Average Intensity')
    time_column = find_column_by_content(path,'Elapsed Time')

    for row_idx in range(2,sheet.max_row):
        if (sheet.cell(row=row_idx + 1, column=1).value) == 'Image Name':
            break
        hr_cell_now = sheet.cell(row=row_idx, column=rate_column).value
        hr_cell_next = sheet.cell(row=row_idx + 1, column=rate_column).value
        hr_cell_now_time = sheet.cell(row=row_idx, column=time_column).value

        if hr_cell_now is None or hr_cell_next is None:
            continue

        if(top_flag):
            if(hr_cell_next > hr_cell_now):
                bottom_dict_array.append({'time':hr_cell_now_time,'rate':hr_cell_now})
                top_flag = False
        else:
            if(hr_cell_next < hr_cell_now):
                top_dict_array.append({'time':hr_cell_now_time,'rate':hr_cell_now})
                top_flag = True

    return top_dict_array,bottom_dict_array

def data_filter(top_list, bottom_list):
    if not top_list or not bottom_list:
        return [], []

    top_max = top_list[0]['rate']
    bottom_min = bottom_list[0]['rate']

    for i in range(len(top_list)):
        rate = top_list[i]['rate']
        if rate >= top_max:
            top_max = rate

    for j in range(len(bottom_list)):
        rate = bottom_list[j]['rate']
        if rate <= bottom_min:
            bottom_min = rate

    mid_rate = (top_max - bottom_min) / 2 + bottom_min
    min_difference = (top_max - bottom_min) * 0.2  # 设置阈值为最大差值的20%

    top_filter_list = []
    bottom_filter_list = []

    if top_list[0]['time'] > bottom_list[0]['time']:
        for i in range(len(bottom_list) - 1):
            tp_rate = top_list[i]['rate']
            bt_rate = bottom_list[i]['rate']
            rate_diff = tp_rate - bt_rate
            if rate_diff < min_difference:
                continue  # 忽略差值小于阈值的点
            if bt_rate < mid_rate and tp_rate > mid_rate:
                bottom_filter_list.append(bottom_list[i])
                top_filter_list.append(top_list[i])
            elif bt_rate > mid_rate:
                left_top = top_list[i - 1]['rate']
                right_top = top_list[i]['rate']
                if left_top > right_top:
                    top_filter_list.append(top_list[i - 1])
                else:
                    top_filter_list.append(top_list[i])
            elif tp_rate < mid_rate:
                left_bottom = bottom_list[i]['rate']
                right_bottom = bottom_list[i + 1]['rate']
                if left_bottom < right_bottom:
                    bottom_filter_list.append(bottom_list[i])
                else:
                    bottom_filter_list.append(bottom_list[i + 1])
    else:
        for i in range(len(bottom_list) - 1):
            tp_rate = top_list[i]['rate']
            bt_rate = bottom_list[i]['rate']
            rate_diff = tp_rate - bt_rate
            if rate_diff < min_difference:
                continue  # 忽略差值小于阈值的点
            if bt_rate < mid_rate and tp_rate > mid_rate:
                bottom_filter_list.append(bottom_list[i])
                top_filter_list.append(top_list[i])
            elif bt_rate > mid_rate:
                left_top = top_list[i]['rate']
                right_top = top_list[i + 1]['rate']
                if left_top > right_top:
                    top_filter_list.append(top_list[i])
                else:
                    top_filter_list.append(top_list[i + 1])
            elif tp_rate < mid_rate:
                left_bottom = bottom_list[i - 1]['rate']
                right_bottom = bottom_list[i]['rate']
                if left_bottom < right_bottom:
                    bottom_filter_list.append(bottom_list[i - 1])
                else:
                    bottom_filter_list.append(bottom_list[i])

    return top_filter_list, bottom_filter_list


def sort_top_list_by_time(top_list):
    # 使用sorted函数进行排序，按time键排序
    sorted_list = sorted(top_list, key=lambda x: x['time'])
    return sorted_list

def data_compute(ori_path):
    pre_top_list = []
    pre_bottom_list = []

    pre_top_list,pre_bottom_list = findHRTB(ori_path)

    top_list = []
    bottom_list = []

    top_list,bottom_list = data_filter(pre_top_list,pre_bottom_list)

    top_list = sort_top_list_by_time(top_list)
    bottom_list = sort_top_list_by_time(bottom_list)

    top_sum = 0
    bottom_sum = 0
    for i in range(len(top_list)-1):
        top_sum += sub_times_in_milliseconds(top_list[i]['time'],top_list[i+1]['time'])
    for j in range(len(bottom_list)-1):
        bottom_sum += sub_times_in_milliseconds(bottom_list[j]['time'],bottom_list[j+1]['time'])

    RR_dis = top_sum/(len(top_list)-1)
    QT_dis = bottom_sum/(len(bottom_list)-1)
    HR = int(len(top_list) * 60000 / time_to_milliseconds(top_list[-1]['time']))
    QTcB = QT_dis/((RR_dis/1000.0) ** 0.5)
    QTcF = QT_dis/((RR_dis/1000.0) ** (1.0/3.0))

    workbook = openpyxl.load_workbook(ori_path)
    sheet = workbook.active

    max_column = sheet.max_column

    sheet.cell(row=1,column=max_column + 2).value = 'RR'
    sheet.cell(row=1,column=max_column + 3).value = 'QT'
    sheet.cell(row=1,column=max_column + 4).value = 'HR'
    sheet.cell(row=1,column=max_column + 5).value = 'QTcB'
    sheet.cell(row=1,column=max_column + 6).value = 'QTcF'

    sheet.cell(row=2,column=max_column + 2).value = RR_dis
    sheet.cell(row=2,column=max_column + 3).value = QT_dis
    sheet.cell(row=2,column=max_column + 4).value = HR
    sheet.cell(row=2,column=max_column + 5).value = QTcB
    sheet.cell(row=2,column=max_column + 6).value = QTcF

    workbook.save(ori_path)
