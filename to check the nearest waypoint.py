import math
#from pymavlink import mavutil
#from pymavlink import mavwp
import os
import numpy as np
from math import sqrt
import builtins
import subprocess
#import re
import time

#declare waypoints path folder
folder_path = "/home/nerdnhk/pymavlink/wpf_folder/"
print(folder_path)
#necessary list declaration
wpf_dis_list = []
wp_att_list = []
file_name_list = os.listdir(folder_path)
print(file_name_list)

#declare a test lat and lon
curr_lat = 13.435455
curr_lon = 77.731476

for file_name in file_name_list:
    file_path = os.path.join(folder_path, file_name)
    if os.path.isfile(file_path):
        with builtins.open(file_path) as f:
            for i, line in enumerate(f):
                if i == 0:
                    if not line.startswith('QGC WPL 110'):
                        raise Exception('File is not supported WP version')
                elif i ==1:
                    linearray = line.split('\t')
                    ln_x = np.float32(linearray[8])
                    ln_y = np.float32(linearray[9])
                    ln_z = float(linearray[10])
                    wpf_dis_list.append(math.sqrt((ln_x-curr_lat)**2+(ln_y-curr_lon)**2))
                    break
    print(file_path)
min_dis = min(wpf_dis_list)
i = 0
for j in wpf_dis_list:
     if min_dis==j:
          near_index = i
          break
     i+=1
Final_wpf = file_name_list[near_index]

print('nearest wp_file is:  '+Final_wpf)

subprocess.Popen(['MissionnPlanner.exe',Final_wpf])

while not os.path.exists(os.path.join(os.getenv('prg'),'Mission Planner','MissionPlanner.exe')):

time.sleep(10)


