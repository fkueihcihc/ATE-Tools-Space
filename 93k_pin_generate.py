#!/usr/bin/python
''' -*- coding: utf-8 -*-
************************************************************
 FileName:93k_pin_generate.py
 Creator: pengbobo <peng.bobo@zte.com.cn>
 Create Time: 2019-06-11
 Description: This is the code for quickly generating
   93k smatest pin file by ATE Script developing team
 CopyRight: Copyright belong to ZTE-ATE team, All rights reserved.
 '''
# Revision: V1.0.0
# usage: python 93k_pin_generate.py [input csv file] [output pin file]
# for example:
# python 93k_pin_generate.py InputPinInfo.csv test.pin
#************************************************************
import os,sys
import re
#************************************************************
# Function Name: parse_pinInfo_csv(input_file,debug)
# Description: This function parse the pin information input
#   csv file
# Parameters:
#  1. input_file is a csv specified format file with pin
#    information
# 2. debug is a flag for contorl output debug log
# Return:
#    dict type group,port,conf are returned
 
#************************************************************
def parse_pinInfo_csv(input_file,debug):
    
 f = open(input_file,'r')  # read the csv file
   
 #************************************************************  
 # declare variables
 #************************************************************
 pinInfo = {} 
 words_key = []
 group = {}
 port = {}
 conf = {'std':[],'SIG':[],'DPS':[]}
 
 #************************************************************  
 # parse the file
 #************************************************************
 for line in f:
  line = line.strip('\n') 
  line = line.strip()
  
  #************************************************************  
  # extract title information
  # create keys
  #************************************************************
  if line.startswith('Pin_Name'): 
   words_key = line.split(',')
   if debug == 1: print(words_key)
   
   for w in words_key:
    pinInfo.setdefault(w,[]) 
   if debug == 1: print(">>>pinInfo define:",pinInfo)
   
  #************************************************************  
  # bypass comment information
  #************************************************************
  
  elif line.startswith('#'): 
   if debug == 1: print("comment information:",line)
   continue
  #************************************************************  
  # assign word value
  # create dict:group/port
  #************************************************************
  else:
   words_value = line.split(',')
   if debug == 1: print(words_value)
   for i in range(0,len(words_key)):  # assign word value
    pinInfo[words_key[i]].append(words_value[i])
  
   if words_value[2].strip() != '': # create group
    group_name = words_value[2].split(';')
    for gName in group_name:
     if not gName in group:
      group[gName] = []
     group[gName].append(words_value[0])
   
   if words_value[3].strip() != '': # create port
    port_name = words_value[3].split(';')
    for pName in port_name:
     if not pName in port:
      port[pName] = []
     port[pName].append(words_value[0])
   
   if words_value[6] == "Digital":
    if words_value[5] == "std":
     conf['std'].append(words_value[0])
    elif words_value[5] == "SIG":
     conf['SIG'].append(words_value[0])
   elif words_value[6] == "DPS":
    conf['DPS'].append(words_value[0])
    
  if debug == 1: print("group:",group)
  if debug == 1: print("port:",port)
  if debug == 1: print("conf:",conf)
      
  f.close()
    
  return group,port,conf
 #************************************************************
 # Function Name: generate_pin(input_file,output_file,group,port,conf,debug)
 # Description: This function generate the pin file
 # Parameters:
 #  1. input_file is a csv specified format file with pin
 #    information
 #  2. output_file is the pin file name needing to generate
 # 3. group is the group name for digital pins
 # 4. port is the port name for digital pins
 # 5. conf is the conf information for digital or DPS pins
 # 6. debug is a flag for contorl output debug log
 # Return:
 #    None
  
 #************************************************************
  
 def generate_pin(input_file,output_file,group,port,conf,debug):
  fin = open(input_file,'r') # open input csv file in read mode
  fout = open(output_file,'w') # open output file in write mode
  pin_head = "hp93000,config,0.1"
  fout.write(pin_head + '\n')
  sites = 1 # set sites default 1
  
  #************************************************************
  
  # analog_pogo_map has the pogo mapping information
  # including all the analog card such as MCA,MCB,MCE,MCL
  
  #************************************************************
  
  analog_pogo_map = {'A+':(1,'i'),'B+':(2,'i') ,'C+':(3,'i'),'D+':(4,'i'),
  'A-':(5,'i'),'B-':(6,'i'),'C-':(7,'i'),'D-':(8,'i'),'E+':(9,'o'),
  'F+':(10,'o'),'G+':(11,'o'),'H+':(12,'o'),'E-':(13,'o'),'F-':(14,'o'),
  'G-':(15,'o'),'H-':(16,'o'),'AA+':(17,'i'),'BB+':(18,'i'),'CC+':(19,'i'),
  'DD+':(20,'i'),'AA-':(21,'i'),'BB-':(22,'i'),'CC-':(23,'i'),'DD-':(24,'i'),
  'EE+':(25,'o'),'FF+':(26,'o'),'GG+':(27,'o'),'HH+':(28,'o'),'EE-':(29,'o'),
  'FF-':(30,'o'),'GG-':(31,'o'),'HH-':(32,'o')}
  
  #************************************************************
  
  # write the pin file line by line 
  
  #************************************************************
  
  for line in fin:
   line = line.strip('\n')
   line = line.strip()
   
   if line.startswith('Pin_Name'): # get the number of sites
    words_value = line.split(',')
    sites = len(words_value) - 8
    if debug == 1: print("sites:",sites)
    continue
    
   elif line.startswith('#'): #bypass the comment line
    continue
   
   else:
    words_value = line.split(',')
    
    #************************************************************
  
    # write the channel number in the file 
   
    #************************************************************
    
    if words_value[6] == "Digital": # process the Digital pins
     for i in range(0,sites):
      if i == 0 :
       fout.write("DFPN ")
      else:
       fout.write("PALS " + str(i+1) + ',')
      fout.write(words_value[8+i])
      fout.write(',')
      if i == 0: fout.write('"' + words_value[1] + '"')
      fout.write(',')
      fout.write('(')
      fout.write(words_value[0])
      fout.write(')')
      fout.write('\n')
      
    elif words_value[6] == "Analog": # process the Analog pins
     for i in range(0,sites):
      if i == 0:
       fout.write("DFAN ") 
      else:
       fout.write("PALS " + str(i+1) + ',')
      ana_info = re.match('.*([0-9]{3}).*(MC\w).*\_(\S{2,3})$',words_value[8+i])
      if debug == 1: print("analog group:",ana_info.groups())
      pogo_block = ana_info.group(2)+ ana_info.group(1)
      mode_value = analog_pogo_map[ana_info.group(3)][0]
      ana_type = analog_pogo_map[ana_info.group(3)][1]
      
      fout.write('"')
      fout.write(pogo_block)
      fout.write(',')
      fout.write(str(mode_value))
      fout.write(',')
      fout.write(ana_type)
      fout.write('"')
      fout.write(',')
      if i == 0: fout.write('"' + words_value[1] + '"')
      fout.write(',')
      fout.write('(')
      fout.write(words_value[0])
      fout.write(')')
      fout.write('\n')
      
    elif words_value[6] == "DPS": # process the DPS pins
     for i in range(0,sites):
      if i == 0:
       fout.write("DFPS ")
      else:
       fout.write("PALS " + str(i+1) + ',')
      if re.search('-', words_value[8+i]):
       fout.write('(')
       dps_channel = re.search('(\d+)-(\d+)', words_value[8+i])
       for j in range(int(dps_channel.group(1)),int(dps_channel.group(2))+1):
        if j != int(dps_channel.group(2)):
         fout.write(str(j) + ',')
        else:
         fout.write(str(j))
       fout.write(')')
      else:
       fout.write(words_value[8+i])
      fout.write(',')
      if i == 0: fout.write('POS')
      fout.write(',')
      fout.write('(')
      fout.write(words_value[0])
      fout.write(')')
      fout.write('\n')
      
    elif words_value[6] == "Utility": # process the Utility pins
     for i in range(0,sites):
      if i == 0:
       fout.write("DFUT ")
      else:
       fout.write("PALS " + str(i+1) + ',')
      uti_no = re.match('UT([1-8]{1}).*([0-3][0-9])',words_value[8+i],re.I)
      uti_channel_no = 1 + int(uti_no.group(1) + uti_no.group(2))
      fout.write(str(uti_channel_no))
      fout.write(',')
      if i == 0: fout.write('RW')
      fout.write(',')
      fout.write('(')
      fout.write(words_value[0])
      fout.write(')')
      fout.write('\n')
    
    fout.flush() # flush the buffer
    
    #************************************************************
  
    # write the comment for the pin 
   
    #************************************************************
    
    if words_value[7].strip() != '':
     fout.write('DFPC (' + words_value[0] + '),"' + words_value[7] + '"\n')
    
  fout.write('PSTE ' + str(sites)) # define the number of sites
  fout.write('\n')
  
  fout.write('CTXT DEFINE,"DEFAULT"\n')
  
  #************************************************************
  
  # write the conf for digital & DPS pin 
  
  #************************************************************
  for key in conf.keys():
   if 'std' == key:
    fout.write('CONF IO,F160,(')
    for i in range(0,len(conf[key])):
     if i == len(conf[key]) - 1: 
      fout.write(conf[key][i] + ')\n')
     else:
      fout.write(conf[key][i] + ',')
   elif 'SIG' == key:
    if len(conf[key]) > 0:
     fout.write('CONF DC,DCSIGNAL,(')
     for i in range(0,len(conf[key])):
      if i == len(conf[key]) - 1: 
       fout.write(conf[key][i] + ')\n')
      else:
       fout.write(conf[key][i] + ',')
   elif 'DPS' == key:
    if len(conf[key]) > 0:
     fout.write('CONF DC,POWER,(')
     for i in range(0,len(conf[key])):
      if i == len(conf[key]) - 1: 
       fout.write(conf[key][i] + ')\n')
      else:
       fout.write(conf[key][i] + ',')
       
  #************************************************************
  
  # write the group for digital pin 
  
  #************************************************************
  
  for key in group.keys():
   fout.write('DFGP X,(')
   for i in range(0,len(group[key])):
    if i == len(group[key]) - 1:
     fout.write(group[key][i] + '),')
    else:
     fout.write(group[key][i] + ',')
   fout.write('(' + key + ')\n')
   
  #************************************************************
  
  # write the port for digital pin 
  
  #************************************************************
  
  for key in port.keys():
   fout.write('DFPT (')
   for i in range(0,len(port[key])):
    if i == len(port[key]) - 1:
     fout.write(port[key][i] + '),')
    else:
     fout.write(port[key][i] + ',')
   fout.write('(' + key + ')\n')
  
  #************************************************************
  
  # write the pin end  
  
  #************************************************************
  
  AnnounceTriggerDomain = 'ACMD "ATRD","1,1",\nACMD "ATRD","C1,1",\nACMD "ATRD","C2,1",\n'
  fout.write(AnnounceTriggerDomain)
    
  fin.close() # close input file
  fout.close() # close output file
  
  return
  
 if __name__ == '__main__':
  input_file = sys.argv[1]
  output_file = sys.argv[2]
  curr_dir = os.getcwd()
  input_file = curr_dir + '/' + input_file
  output_file = curr_dir + '\\' + output_file
  print("input file:> ",input_file)
  group,port,conf = parse_pinInfo_csv(input_file,0)
  print("output file:< ",output_file)
  generate_pin(input_file,output_file,group,port,conf,0)
