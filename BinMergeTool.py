#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import re
#import csv
#import tkinter

''' 
************************************************************
 FileName:BinMergeTool.py
 Creator: pengbobo <bobo.peng@bitmain.com>
 Create Time: 2022-03-24
 Description: This script is for quickly merge bin file
 CopyRight: Copyright belong to bitmain ATE team, All rights reserved.
 '''
# Revision: V1.0.0
# usage: ./BinMergeTool.py
# ************************************************************

# ************************************************************
# declare global var
debug = 0
write_header = 1
base_num = -999999
'''
class name: BinInfo
Description: This class define a data structure including (paht,file_list)
'''
class BinInfo:
    __slots__ = ["path","file_list"]
    def __init__(self,p,f):
        self.path,self.file_list = p,f
"""
Function Name: get_binsum_file()
Description: This function is to get the .sum filename input
"""
def get_binsum_file(debug):
    # declare variables
    BI_list = []
    for root,dirs,files in os.walk('.'):
        path = root
        sum_file = []
        for f in files:
          if f.endswith('.sum'):
            sum_file.append(f)
        if [] != sum_file:
          BI = BinInfo(path,sum_file)
          BI_list.append(BI)
    if debug:
        for bi in BI_list:
            print('path:',bi.path)
            print('files:',bi.file_list)
    return BI_list

"""
Function Name: parse_1rst_binsum()
Description: This function is to parse the first test sum file
including test time,program,lot and so on
"""
def parse_1rst_binsum(sum_file, debug):
    flag_sb = 0 # softbin judge
    flag_hb = 0 # hardbin judge
    SBins = {}
    HBins = {'BIN1':'0','BIN2':'0','BIN3':'0','BIN4':'0','BIN5':'0',
             'BIN6':'0','BIN7':'0','BIN8':'0','BIN9':'0'}
    tstInfo = []
    f = open(sum_file, 'r')  # read the sum file
    for line in f:
        line = line.strip('\n')
        line = line.strip()
        if not len(line):
            continue
        if line.startswith('Started at:'):
            test_info = re.match('.*([0-9]{4}\-[0-9]{2}\-[0-9]{2}).*', line)
            test_time = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('test time:',test_time)
            continue
        if line.startswith('Program: '):
            test_info = re.search('^Program:\s+(\w*)\.\w*', line)
            program = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('program:',program)
            continue
        if line.startswith('DEV:'):
            test_info = re.search('(\d+)', line)
            total_num = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if [] == re.findall('B[1-5]C[1-2]',sum_file):
                global base_num
                base_num = int(total_num)
                if debug: print('base_num:',base_num)
            if debug: print('total_num:',total_num)
            continue
        if line.startswith('CUST: '):
            test_info = re.search('^CUST:\s+(\w*)', line)
            cust = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('cust:',cust)
            continue
        if line.startswith('Lot: '):
            test_info = re.match('^Lot:\s*(\S*)', line)
            lot = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('lot:',lot)
            continue
        if line.startswith('SUB: '):
            test_info = re.match('^SUB:\s*(\S*)', line)
            sub = test_info.group(1)
            tstInfo.append(test_info.group(1))
            if debug: print('sub:',sub)
            continue
        if line.startswith('Total Number of devices'):
            flag_sb = 0
            flag_hb = 0
            continue
        if re.findall('SOFTWARE  BIN  TOTALS',line):
            flag_sb = 1
            flag_hb = 0
            continue
        if re.findall('HARDWARE  BIN  TOTALS',line):
            flag_hb = 1
            flag_sb = 0
            continue
        if 1 == flag_sb and 0 == flag_hb:
            if re.search('\d+',line):
                sb_list = line.split()
                SBins.setdefault('BIN'+sb_list[0],'')
                for i in range(2,len(sb_list)-1):
                    SBins['BIN'+sb_list[0]] = (sb_list[i])
            continue
        if 1 == flag_hb and 0 == flag_sb:
            if re.search('\d+',line):
                hb_list = line.split()
                HBins['BIN'+hb_list[0]] = hb_list[2]
            continue

    return tstInfo,dict(sorted(HBins.items()))
"""
Function Name: parse_retest_binsum()
Description: This function is to parse the retest sum file
to get the bin info
"""
def parse_retest_binsum(sum_file, debug):
    flag_sb = 0 # softbin judge
    flag_hb = 0 # hardbin judge
    SBins = {}
    HBins = {'BIN1':'0','BIN2':'0','BIN3':'0','BIN4':'0','BIN5':'0',
             'BIN6':'0','BIN7':'0','BIN8':'0','BIN9':'0'}
    f = open(sum_file, 'r')  # read the sum file
    for line in f:
        line = line.strip('\n')
        line = line.strip()
        if not len(line): # jump space line
            continue
        if re.findall('SOFTWARE  BIN  TOTALS',line):
            flag_sb = 1
            flag_hb = 0
            continue
        if re.findall('HARDWARE  BIN  TOTALS',line):
            flag_hb = 1
            flag_sb = 0
            continue
        if line.startswith('Total Number of devices'):
            flag_sb = 0
            flag_hb = 0
            continue
        if 1 == flag_sb and 0 == flag_hb:
            if re.search('\d+',line):
                sb_list = line.split()
                SBins.setdefault('BIN'+sb_list[0],'')
                for i in range(2,len(sb_list)-1):
                    SBins['BIN'+sb_list[0]] = (sb_list[i])
            continue
        if 1 == flag_hb and 0 == flag_sb:
            if re.search('\d+',line):
                hb_list = line.split()
                HBins['BIN'+hb_list[0]] = hb_list[2]
            continue

    return dict(sorted(HBins.items()))


"""
Function Name: rate_calculator()
Description: This function is to calculate the bin pass/fail rate
"""
def rate_calculator(test_result):
    # bin rate calculate
    global base_num
    total_num = 0
    for i in range(1,9):
        total_num +=int(test_result['BIN'+str(i)])
    if -999999 == base_num:
        base_num = total_num
    if total_num > int(test_result['Total number']):
        os_sub = total_num - int(test_result['Total number'])
        if int(test_result['BIN8']) - os_sub < 0:
            test_result['BIN8'] = '0'
        else:
            test_result['BIN8'] = str(int(test_result['BIN8']) - os_sub)
    bin1_num = int(test_result['BIN1'])
    bin1_rate = round(100.00 * int(test_result['BIN1']) / base_num, 1)
    test_result['bin1%'] = str(bin1_rate) + '%'
    bin2_num = int(test_result['BIN2'])
    bin2_rate = round(100.00 * int(test_result['BIN2']) / base_num, 1)
    test_result['bin2%'] = str(bin2_rate) + '%'
    bin3_num = int(test_result['BIN3'])
    bin3_rate = round(100.00 * int(test_result['BIN3']) / base_num, 1)
    test_result['bin3%'] = str(bin3_rate) + '%'
    bin4_num = int(test_result['BIN4'])
    bin4_rate = round(100.00 * int(test_result['BIN4']) / base_num, 1)
    test_result['bin4%'] = str(bin4_rate) + '%'
    bin5_num = int(test_result['BIN5'])
    bin5_rate = round(100.00 * int(test_result['BIN5']) / base_num, 1)
    good_num = bin1_num + bin2_num + bin3_num + bin4_num + bin5_num
    test_result['bin5%'] = str(bin5_rate) + '%'
    Fail_num = total_num - good_num
    Fail_rate = round(100.00*Fail_num/base_num, 1)
    test_result['Fail%'] = str(Fail_rate) + '%'
    Yield_rate = round(100.00*good_num/base_num, 1)
    test_result['Total Yield%'] = str(Yield_rate) + '%'

    return test_result
"""
Function Name: write2csv()
Description: This function is to write all the info needed into csv file
"""
def write2csv(test_result,csv):
    # write into csv file
    global  write_header
    fout = open(csv, 'a')  # open output file in write mode
    if write_header:
        for key in test_result.keys():
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
        os.rename(file,file)
        print("the file %s is not used,you can use it!!!"%file)
        return True
    except:
        print("the file %s is open,please close it!!!"%file)
        return False
# the main function
if __name__ == '__main__':
    BI_list = get_binsum_file(debug)
    csv = 'ATE_Test_Result.csv'
    if check_if_open(csv):
        fout = open(csv, 'w')
    else:
        csv = "ATE_Test_Result(1).csv"
        fout = open(csv, 'w')
    test_result = {}
    PASS_BINS = ['BIN1','BIN2','BIN3','BIN4','BIN5']
    OS_BIN = 'BIN8'
    for bi in BI_list:
        path = bi.path
        if debug: print('path:',bi.path)
        if debug: print('file number:',len(bi.file_list))
        for sum_file in bi.file_list:
            # first test file
            if debug:  print("Input file:",sum_file)
            sum_file = path + '\\' + sum_file
            if '-FT-' in sum_file:
                tstInfo,HBins = parse_1rst_binsum(sum_file, debug)
                test_head = ['Test time','Program','Mark','Lot','Sub','Total number']
                for i in test_head:
                    test_result.setdefault(i, '')
                for i,j in zip([0,1,2,3,4,5],[1,2,4,0,5,3]): # sort the informaiton
                    test_result[test_head[i]] = (tstInfo[j])
                test_result.update(HBins)
                yield_info = {'bin1%':'','bin2%':'','bin3%':'','bin4%':'','bin5%':'',
                                'Fail%':'','Total Yield%':'','Notes':''}
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
                else: # more than 1 retest times
                    for hb in HBins.keys():
                        if OS_BIN == hb: # OS BIN：replace
                            tmp_num = int(HBins[hb])
                            test_result[hb] = str(tmp_num)
                        else: # None OS BIN: accumulate
                            tmp_num = int(test_result[hb]) + int(HBins[hb])
                            test_result[hb] = str(tmp_num)
        # bin rate calculate
        tmp_result = rate_calculator(test_result)
        test_result.update(tmp_result)
        # write into csv file
        write2csv(test_result,csv)
        write_header = 0
    print("Output file:",csv)
    print(">>>>>>Process Done!")
