import csv
from math import sqrt
import numpy as np
import pandas as pd

file_dis_list = []
curr_lat = np.float32(0)
curr_lon = np.float32(0)

def iterate_csv_fields(csv_filename):
    df = pd.read_csv(csv_filename, usecols=['dont_know_1', 'latitude','longitude'])
    #print(df['dont_know_1'])
    f_lat = np.float32(0)
    f_lon = np.float32(0)
    #print(f_lat)
    for mode in enumerate(df['dont_know_1']):
        row = df.loc[16, :]
        #print(row)
        if f_lat == 0.0 and f_lon == 0.0:
            #print(row)
            f_lat = row.loc['latitude']
            print(f_lat)
            f_lon = row.loc['longitude']
            print(f_lon)
            break
    dis = sqrt((f_lat-curr_lat)**2+(f_lon-curr_lon)**2)
    #print(dis)
    file_dis_list.append(dis)

iterate_csv_fields('Waypoint.csv')
print(file_dis_list)
