import os
#import time
import pandas as pd
from math import sqrt
import numpy as np

# set the directory where the .waypoints files are located
waypoints_dir = '/home/pymavlink/wpf_folder/'

# set the directory where the output .csv files will be saved
csv_dir = '/home/pymavlink/csv_files/'
# necessary declaration
file_dis_list = []
curr_lat = np.float32(0)
curr_lon = np.float32(0)
#final waypoint file
wpf_final = ""

for filename in os.listdir(waypoints_dir):
    if filename.endswith('.waypoints'):
        #uncomment below once to create a new directory, then uncomment it
        #os.mkdir(csv_dir)
        #time.sleep(2)
        
        # read the file into a pandas dataframe
        df = pd.read_csv(os.path.join(waypoints_dir, filename), delimiter='\t', header=None, names=['waypoint_number', 'ishome','confirmation', 'dont_know_1','param_1', 'param_2', 'param_3', 'param_4', 'latitude', 'longitude', 'altitude','dont_know_2'])

        # select specific columns from the dataframe
        selected_columns = df[['waypoint_number', 'ishome','confirmation', 'dont_know_1','param_1', 'param_2', 'param_3', 'param_4', 'latitude', 'longitude', 'altitude','dont_know_2']]

        # construct the output filename
        output_filename = os.path.splitext(filename)[0] + '.csv'

        # write the selected columns to a new .csv file
        selected_columns.to_csv(os.path.join(csv_dir, output_filename), index=False)

def ext_gps(csv_file_path):
    df = pd.read_csv(csv_file_path, usecols=['dont_know_1', 'latitude','longitude'])
    #print(df['dont_know_1'])
    f_lat = np.float32(0)
    f_lon = np.float32(0)
    #print(f_lat)
    for i in range(1,3):
        row = df.loc[i, :]
        #print(row['dont_know_1'])
        if row['dont_know_1'] !=22 and row.loc['latitude'] != 0.0 and row.loc['latitude'] !=0.0:
            #print(row)
            f_lat = row.loc['latitude']
            #print(f_lat)
            f_lon = row.loc['longitude']
            #print(f_lon)
            break
    dis = sqrt((f_lat-curr_lat)**2+(f_lon-curr_lon)**2)
    #print(dis)
    file_dis_list.append(dis)
    

file_name_list = os.listdir(csv_dir)
print(file_name_list)
for file_name in file_name_list:
    csv_file_path = os.path.join(csv_dir,file_name)
    if os.path.isfile(csv_file_path):
        print(file_name+" CSV file found")
        ext_gps(csv_file_path)
    else:
        print("CSV file not found")
# to find the shortest distance
def final_wpf():
    min_dis_wpf = min(file_dis_list)
    pd_series = pd.Series(file_dis_list)
    min_dis_index = pd_series.index[pd_series == min_dis_wpf][0]
    print("The shortest distance wp file:"+str(min_dis_index))
    #print(pd_series)
    wpf_final = file_name_list[min_dis_index]
    print("Final WP file seleted: "+wpf_final)

    # delete the directory
    for file_name in file_name_list:
         csv_file_path = os.path.join(csv_dir,file_name)
         os.remove(csv_file_path)
    #os.rmdir(csv_dir)
         

final_wpf()

