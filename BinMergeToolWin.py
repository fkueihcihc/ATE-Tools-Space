#!/usr/bin/python
import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory
import time
import re
import os

''' 
************************************************************
 FileName:BinLabelPrint.py
 Creator: pengbobo <bobo.peng@bitmain.com>
 Create Time: 2022-04-02
 Upgrade Time: 2022-05-12
 Description: This script is for quickly printing FT production Label
 CopyRight: Copyright belong to bitmain ATE team, All rights reserved.
 '''
# Revision: V2.0.0
# usage: GUI
# ************************************************************

# declare global var
debug = 0
write_header = 1
base_num = -999999
LOG_LINE_NUM = 0

'''
class name: BinInfo
Description: This class define a data structure including (paht,file_list)
'''
class BinInfo:
    __slots__ = ["path", "file_list"]

    def __init__(self, p, f):
        self.path, self.file_list = p, f
"""
Function Name: takeFirst()
Description: This function is to sort by first element
"""
def takeFirst(elem):
    return elem.path
"""
Function Name: get_binsum_file()
Description: This function is to get the .sum filename input
"""
def get_binsum_file(path,debug):
    # declare variables
    BI_list = []
    for root, dirs, files in os.walk(path):
        path = root
        sum_file = []
        for f in files:
            if f.endswith('.sum'):
                sum_file.append(f)
        if [] != sum_file:
            sum_file.sort()
            BI = BinInfo(path, sum_file)
            BI_list.append(BI)
    BI_list.sort(key=takeFirst)
    if debug:
        for bi in BI_list:
            print('path:', bi.path)
            print('files:', bi.file_list)

    return BI_list
"""
Function Name: parse_1rst_binsum()
Description: This function is to parse the first test sum file
including test time,program,lot and so on
"""
def parse_1rst_binsum(sum_file, debug):
    flag_sb = 0  # softbin judge
    flag_hb = 0  # hardbin judge
    SBins = {}
    HBins = {'BIN1': '0', 'BIN2': '0', 'BIN3': '0', 'BIN4': '0', 'BIN5': '0',
             'BIN6': '0', 'BIN7': '0', 'BIN8': '0', 'BIN9': '0'}
    tstInfo = []
    f = open(sum_file, 'r')  # read the sum file
    for line in f:
        line = line.strip('\n')
        line = line.strip()
        if not len(line):
            continue
        if line.startswith('Lot: '): #lot id
            test_info = re.match('^Lot:\s*(\S*)', line)
            lot = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('lot:', lot)
            continue
        if line.startswith('Started at:'): #test time
            test_info = re.match('.*([0-9]{4}\-[0-9]{2}\-[0-9]{2}).*', line)
            test_time = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('test time:', test_time)
            continue
        if line.startswith('Program: '):
            test_info = re.search('^Program:\s+(\w+)', line)
            program = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('program:', program)
            continue
        if line.startswith('Tester: '):
            test_info = re.search('^Tester:\s+(\w+)', line)
            tester = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('tester:', tester)
            continue
        if line.startswith('CUST: '): # Marking
            test_info = re.search('^CUST:\s+(\w*)', line)
            cust = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('cust:', cust)
            continue
        if line.startswith('SUB: '): # sub
            test_info = re.match('^SUB:\s*(\S*)', line)
            sub = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('sub:', sub)
            continue
        if line.startswith('TCCT_RDY: '): #ERPCODE
            test_info = re.match('^TCCT_RDY:\s*(\S*)', line)
            erpcode = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('erpcode:', erpcode)
            continue
        if line.startswith('Total Number of devices'):
            test_info = re.search('(\d+)', line)
            total_num = test_info.group(1)
            tstInfo.append(test_info.group(1))
            flag_sb = 0
            flag_hb = 0
            if [] == re.findall('B[1-5]C[1-2]', sum_file):
                global base_num
                base_num = int(total_num)
                if debug: print('base_num:', base_num)
            if debug: print('total_num:', total_num)
            continue
        if re.findall('SOFTWARE  BIN  TOTALS', line):
            flag_sb = 1
            flag_hb = 0
            continue
        if re.findall('HARDWARE  BIN  TOTALS', line):
            flag_hb = 1
            flag_sb = 0
            continue
        if 1 == flag_sb and 0 == flag_hb:
            if re.search('\d+', line):
                sb_list = line.split()
                SBins.setdefault('BIN' + sb_list[0], '')
                for i in range(2, len(sb_list) - 1):
                    SBins['BIN' + sb_list[0]] = (sb_list[i])
            continue
        if 1 == flag_hb and 0 == flag_sb:
            if re.search('\d+', line):
                hb_list = line.split()
                HBins['BIN' + hb_list[0]] = hb_list[-2]
            continue

    return tstInfo, dict(sorted(HBins.items()))
"""
Function Name: parse_retest_binsum()
Description: This function is to parse the retest sum file
to get the bin info
"""

def parse_retest_binsum(sum_file, debug):
    flag_sb = 0  # softbin judge
    flag_hb = 0  # hardbin judge
    SBins = {}
    HBins = {'BIN1': '0', 'BIN2': '0', 'BIN3': '0', 'BIN4': '0', 'BIN5': '0',
             'BIN6': '0', 'BIN7': '0', 'BIN8': '0', 'BIN9': '0'}
    f = open(sum_file, 'r')  # read the sum file
    for line in f:
        line = line.strip('\n')
        line = line.strip()
        if not len(line):  # jump space line
            continue
        if re.findall('SOFTWARE  BIN  TOTALS', line):
            flag_sb = 1
            flag_hb = 0
            continue
        if re.findall('HARDWARE  BIN  TOTALS', line):
            flag_hb = 1
            flag_sb = 0
            continue
        if line.startswith('Total Number of devices'):
            flag_sb = 0
            flag_hb = 0
            continue
        if 1 == flag_sb and 0 == flag_hb:
            if re.search('\d+', line):
                sb_list = line.split()
                SBins.setdefault('BIN' + sb_list[0], '')
                for i in range(2, len(sb_list) - 1):
                    SBins['BIN' + sb_list[0]] = (sb_list[i])
            continue
        if 1 == flag_hb and 0 == flag_sb:
            if re.search('\d+', line):
                hb_list = line.split()
                HBins['BIN' + hb_list[0]] = hb_list[-2]
            continue

    return dict(sorted(HBins.items()))
"""
Function Name: rate_calculator()
Description: This function is to calculate the bin pass/fail rate
"""
def rate_calculator(test_result,OS_BIN,PASS_BINS):
    # bin rate calculate
    global base_num
    total_num = 0
    good_num = 0
    for i in range(1, 9):
        total_num += int(test_result['BIN' + str(i)])
    if -999999 == base_num:
        base_num = total_num
    if total_num > int(test_result['Total number']):
        os_sub = total_num - int(test_result['Total number'])
        if int(test_result[OS_BIN]) - os_sub < 0:
            test_result[OS_BIN] = '0'
        else:
            test_result[OS_BIN] = str(int(test_result[OS_BIN]) - os_sub)
    # pass bin rate calculate
    for bin in PASS_BINS:
        good_num += int(test_result[bin])
        bin_rate = round(100.00 * int(test_result[bin]) / base_num, 1)
        test_result[bin.lower()+'%'] = str(bin_rate) + '%'
    # print('pass bin', PASS_BINS)
    # print('total number', base_num)
    # print('pass number',good_num)
    # fail bin rate calculate
    Fail_num = total_num - good_num
    # print('fail number', Fail_num)
    Fail_rate = round(100.00 * Fail_num / base_num, 1)
    test_result['Fail%'] = str(Fail_rate) + '%'
    # Yield rate calculate
    Yield_rate = round(100.00 * good_num / base_num, 1)
    test_result['Total Yield%'] = str(Yield_rate) + '%'

    return test_result
"""
Function Name: write2csv()
Description: This function is to write all the info needed into csv file
"""
def write2csv(test_result, csv):
    # write into csv file
    global write_header
    fout = open(csv, 'a')  # open output file in write mode
    if write_header:
        for key in test_result.keys():
            #转中文输出
            if 'Test time' == key:
                fout.write('测试时间')
                fout.write(',')
            elif 'Tester' == key:
                fout.write('测试机台')
                fout.write(',')
            elif 'Erpcode' == key:
                fout.write('ERPCODE')
                fout.write(',')
            elif 'Program' == key:
                fout.write('软件版本')
                fout.write(',')
            elif 'Mark' == key:
                fout.write('型号')
                fout.write(',')
            elif 'Sub' == key:
                fout.write('批次')
                fout.write(',')
            elif 'Total number' == key:
                fout.write('总颗数')
                fout.write(',')
            else:
                fout.write(key)
                fout.write(',')
        fout.write('\n')
        write_header = 0
    for value in test_result.values():
        fout.write(value)
        fout.write(',')
    fout.write('\n')
    fout.close()
"""
Function Name: check_if_open()
Description: This function is to check if file is open before write into it
"""
def check_if_open(file):
    try:
        os.rename(file, file)
        print("the file %s is not used,you can use it!!!" % file)
        return True
    except:
        print("the file %s is open,please close it!!!" % file)
        return False

class MY_GUI():
    def __init__(self,init_window_name,path1,path2):
        self.init_window_name = init_window_name
        self.path1,self.path2 = path1,path2
    #设置窗口
    def set_init_window(self):
        self.init_window_name.title("BIN合并工具V2.0 ©2022 Bitmain")           #窗口名
        self.init_window_name.geometry('410x300+10+10')                  #438x312为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        # self.init_window_name.geometry('1024x768+10+10')
        # self.init_window_name["bg"] = "Snow"
        # self.init_window_name.attributes("-alpha",0.9)           #虚化，值越小虚化程度越高
        #标签
        self.log_label = Label(self.init_window_name, text="",font = ('宋体',12))
        self.log_label.grid(row=2, column=2)

        # 日志
        self.log_data_Text = Text(self.init_window_name, width=63, height=20, background="white", fg="black")  # 日志框
        self.log_data_Text.grid(row=13, column=0, columnspan=12,rowspan=13)
        self.log_error_Text = Text(self.init_window_name, width=63, height=5, background="white", fg="red")  # 报错日志框
        self.log_error_Text.grid(row=20, column=0, columnspan=12,rowspan=5)


        # #标签
        # self.init_data_label = Label(self.init_window_name, text="选择目录")
        # self.init_data_label.grid(row=0, column=0, rowspan=1, columnspan=1)
        # 导入目录
        self.init_data_entry = Entry(self.init_window_name, width=16,textvariable= self.path1)
        self.init_data_entry.grid(row=1, column=0,rowspan=1, columnspan=1)
        #按钮
        self.init_result_button = Button(self.init_window_name,font = ('宋体',10), text="选择LOG文件夹", bg="lightgrey",
                                         width=12,command=self.selectPath)
        self.init_result_button.grid(row=1,column=1,columnspan=1,sticky=tkinter.W)
        # # 标签
        # self.init_result_label = Label(self.init_window_name, text="保存文件")
        # self.init_result_label.grid(row=0, column=6, rowspan=1, columnspan=1)
        # 导出目录
        self.init_result_entry = Entry(self.init_window_name, width=16,textvariable= self.path2)
        self.init_result_entry.grid(row=1, column=3,rowspan=1, columnspan=1)
        #按钮
        self.init_result_button = Button(self.init_window_name,font = ('宋体',10), text="保存为csv", bg="lightgrey",
                                         width=8,command=self.save_file)
        self.init_result_button.grid(row=1, column=2, columnspan=1, sticky=tkinter.W)

        # PASS BIN标签
        self.init_passbin_label = Label(self.init_window_name, text="PASS BIN编号")
        self.init_passbin_label.grid(row=2, column=1, columnspan=1)
        # 输入BIN信息
        self.init_passbin_entry = Entry(self.init_window_name, width=16)
        self.init_passbin_entry.grid(row=2, column=0, rowspan=1, columnspan=1)

        # OS BIN标签
        self.init_osbin_label = Label(self.init_window_name, text="OS BIN编号")
        self.init_osbin_label.grid(row=2, column=2, columnspan=1)
        # 输入BIN信息
        self.init_osbin_entry = Entry(self.init_window_name, width=16)
        self.init_osbin_entry.grid(row=2, column=3, rowspan=1, columnspan=1)

        #按钮
        self.sum2csv_button = Button(self.init_window_name,font = ('隶书',18,'bold'),fg = 'white',activeforeground =
        'red',relief=RAISED,justify =CENTER, highlightcolor = 'red' ,text="开始合并", bg="LimeGreen", height=1,width=8,
        command=self.sum2csv_button)  # 调用内部方法  加()为直接调用
        self.sum2csv_button.grid(row=3, column=1,rowspan=1,columnspan=2)

    # 选择路径
    def selectPath(self):
        path_ = askdirectory()
        self.path1.set(path_)

    def save_file(self):
        path_ = filedialog.asksaveasfilename(title=u'保存文件')
        self.path2.set(path_)

    #功能函数
    def sum2csv_button(self):
        global write_header,debug,LOG_LINE_NUM,base_num
        inputdir = self.init_data_entry.get()
        savefile = self.init_result_entry.get()
        pass_bins = self.init_passbin_entry.get()
        os_bin =  self.init_osbin_entry.get()
        if inputdir:
            try:
                self.write_log_to_Text("导入目录："+inputdir)
                self.write_log_to_Text("输出文件："+savefile)
                # self.BinMerge(inputdir, savefile)
                BI_list = get_binsum_file(inputdir, debug)
                csv = savefile
                fout = open(csv, 'w')
                test_result = {}
                PASS_BINS = []
                # PASS_BINS = ['BIN1', 'BIN2', 'BIN3', 'BIN4', 'BIN5']
                if pass_bins:
                    BINS = pass_bins.split(',')
                    for bin in BINS:
                        PASS_BINS.append('BIN'+bin)
                else: # default PASS BIN set
                    PASS_BINS = ['BIN1', 'BIN2', 'BIN3', 'BIN4']
                if os_bin:
                    OS_BIN = 'BIN'+ os_bin
                else:#default OS BIN set
                    OS_BIN = 'BIN8'
                # OS_BIN = 'BIN8'
                for bi in BI_list:
                    path = bi.path
                    if debug: print('path:', bi.path)
                    if debug: print('file number:', len(bi.file_list))
                    for sum_file in bi.file_list:
                        # first test file
                        # self.write_log_to_Text("Input file:"+sum_file)
                        if debug:  print("Input file:", sum_file)
                        sum_file = path + '\\' + sum_file
                        if '-FT-' in sum_file:
                            tstInfo, HBins = parse_1rst_binsum(sum_file, debug)
                            test_head = ['Test time', 'Tester','Erpcode','Program', 'Mark', 'Lot', 'Sub', 'Total number']
                            for i in test_head:
                                test_result.setdefault(i, '')
                            for i, j in zip([0,1,2,3,4,5,6,7], [1,3,6,2,4,0,5,7]):  # sort the information
                                test_result[test_head[i]] = (tstInfo[j])
                            test_result.update(HBins)
                            yield_info = {'bin1%': '0.00%', 'bin2%': '0.00%', 'bin3%': '0.00%', 'bin4%': '0.00%',
                                          'bin5%': '0.00%','Fail%': '0.00%', 'Total Yield%': '0.00%', 'Notes': ''}
                            test_result.update(yield_info)
                        elif '-RT' in sum_file:
                            HBins = parse_retest_binsum(sum_file, debug)
                            # merge hardbin
                            if '-RT-' in sum_file:
                                for hb in HBins.keys():
                                    if hb in PASS_BINS:
                                        tmp_num = int(test_result[hb]) + int(HBins[hb])
                                        test_result[hb] = str(tmp_num)
                                    else:
                                        tmp_num = int(HBins[hb])
                                        test_result[hb] = str(tmp_num)
                            else:  # more than 1 retest times
                                for hb in HBins.keys():
                                    if OS_BIN == hb:  # OS BIN：replace
                                        tmp_num = int(HBins[hb])
                                        test_result[hb] = str(tmp_num)
                                    else:  # None OS BIN: accumulate
                                        tmp_num = int(test_result[hb]) + int(HBins[hb])
                                        test_result[hb] = str(tmp_num)
                    # bin rate calculate
                    tmp_result = rate_calculator(test_result,OS_BIN,PASS_BINS)
                    test_result.update(tmp_result)
                    # write into csv file
                    write2csv(test_result, csv)
                # reset flag
                write_header = 1
                debug = 0
                base_num = -999999
                LOG_LINE_NUM = 0

                # process finished
                self.write_log_to_Text("输出文件:"+csv)
                self.write_log_to_Text(">>>>>>处理完成!")
                # print("Output file:", csv)
                # print(">>>>>>Process Done!")
            except:
                self.write_error_to_Text("错误:请选择输出文件或该文件已打开！！！")
        else:
            self.write_error_to_Text("错误:请选择导入目录或输出文件！！！")
    #获取当前时间
    def get_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        return current_time

    #日志动态打印
    def write_log_to_Text(self,logmsg):
        global LOG_LINE_NUM
        current_time = self.get_current_time()
        logmsg_in = str(current_time) +" " + str(logmsg) + "\n"      #换行
        if LOG_LINE_NUM <= 120:
            self.log_data_Text.insert(END, logmsg_in)
            LOG_LINE_NUM = LOG_LINE_NUM + 1
        else:
            self.log_data_Text.delete(1.0,2.0)
            self.log_data_Text.insert(END, logmsg_in)

    #日志动态打印
    def write_error_to_Text(self,logmsg):
        global LOG_LINE_NUM
        current_time = self.get_current_time()
        logmsg_in = str(current_time) +" " + str(logmsg) + "\n"      #换行
        if LOG_LINE_NUM <= 120:
            self.log_error_Text.insert(END, logmsg_in)
            LOG_LINE_NUM = LOG_LINE_NUM + 1
        else:
            self.log_error_Text.delete(1.0,2.0)
            self.log_error_Text.insert(END, logmsg_in)

# the main function
if __name__ == '__main__':
    if 1:
        init_window = Tk()              #实例化出一个父窗口
        path1 = StringVar()
        path2 = StringVar()
        ZMJ_PORTAL = MY_GUI(init_window,path1,path2)
        # 设置根窗口默认属性
        ZMJ_PORTAL.set_init_window()
        init_window.mainloop()          #父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示
    if 0:
        inputdir = r"D:\01_myWork\02_ScriptsDev\BinLabelPrint\BM1764AB\20220224"
        savefile = r"D:\01_myWork\02_ScriptsDev\BinLabelPrint\BM1764AB\20220224\123.csv"
        BI_list = get_binsum_file(inputdir, debug)
        csv = savefile
        fout = open(csv, 'w')
        test_result = {}
        PASS_BINS = []
        PASS_BINS = ['BIN1', 'BIN2', 'BIN3', 'BIN4']
        # if pass_bins:
        #     BINS = pass_bins.split(',')
        #     for bin in BINS:
        #         PASS_BINS.append('BIN' + bin)
        # else:  # default PASS BIN set
        #     PASS_BINS = ['BIN1', 'BIN2', 'BIN3', 'BIN4']
        # if os_bin:
        #     OS_BIN = 'BIN' + os_bin
        # else:  # default OS BIN set
        #     OS_BIN = 'BIN8'
        OS_BIN = 'BIN8'
        for bi in BI_list:
            path = bi.path
            if debug: print('path:', bi.path)
            if debug: print('file number:', len(bi.file_list))
            for sum_file in bi.file_list:
                # first test file
                # self.write_log_to_Text("Input file:"+sum_file)
                if debug:  print("Input file:", sum_file)
                sum_file = path + '\\' + sum_file
                if '-FT-' in sum_file:
                    tstInfo, HBins = parse_1rst_binsum(sum_file, debug)
                    test_head = ['Test time', 'Tester', 'Erpcode', 'Program', 'Mark', 'Lot', 'Sub', 'Total number']
                    for i in test_head:
                        test_result.setdefault(i, '')
                    for i, j in zip([0, 1, 2, 3, 4, 5, 6, 7], [1, 3, 6, 2, 4, 0, 5, 7]):  # sort the informaiton
                        test_result[test_head[i]] = (tstInfo[j])
                    test_result.update(HBins)
                    yield_info = {'bin1%': '0%', 'bin2%': '0%', 'bin3%': '0%', 'bin4%': '0%', 'bin5%': '0%',
                                  'Fail%': '0%', 'Total Yield%': '0%', 'Notes': ''}
                    test_result.update(yield_info)
                elif '-RT' in sum_file:
                    HBins = parse_retest_binsum(sum_file, debug)
                    # merge hardbin
                    if '-RT-' in sum_file:
                        for hb in HBins.keys():
                            if hb in PASS_BINS:
                                tmp_num = int(test_result[hb]) + int(HBins[hb])
                                test_result[hb] = str(tmp_num)
                            else:
                                tmp_num = int(HBins[hb])
                                test_result[hb] = str(tmp_num)
                    else:  # more than 1 retest times
                        for hb in HBins.keys():
                            if OS_BIN == hb:  # OS BIN：replace
                                tmp_num = int(HBins[hb])
                                test_result[hb] = str(tmp_num)
                            else:  # None OS BIN: accumulate
                                tmp_num = int(test_result[hb]) + int(HBins[hb])
                                test_result[hb] = str(tmp_num)
            # bin rate calculate
            tmp_result = rate_calculator(test_result,OS_BIN,PASS_BINS)
            test_result.update(tmp_result)
            # write into csv file
            write2csv(test_result, csv)
        # reset flag
        write_header = 1
        debug = 0
        base_num = -999999
        LOG_LINE_NUM = 0