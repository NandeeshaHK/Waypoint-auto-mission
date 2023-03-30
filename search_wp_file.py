import math
from pymavlink import mavutil
from pymavlink import mavwp
import os
import numpy as np
from math import sqrt
import re
import time

# Start a connection listening on a UDP port
the_connection = mavutil.mavlink_connection('udpin:localhost:14551')

# Wait for the first heartbeat 
#   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))
wp = mavwp.MAVWPLoader()

# Once connected, use 'the_connection' to get and send messages
msg = the_connection.recv_match(type="TERRAIN_REPORT",blockings = True)
print(msg)
lat_pattern = re.compile(r'lat:\s*([-\d.]+)')
lon_pattern = re.compile(r'lon:\s*([-\d.]+)')
lat_match = lat_pattern.search(msg)
lon_match = lon_pattern.search(msg)
curr_lat = np.uint32(lat_match)
curr_lon = np.uint32(lon_match)
home_location = (curr_lat,curr_lon)
near_index = 0


#declare waypoints path folder
folder_path = "/pymavlink/"
#necessary list declaration
wpf_dis_list = []
wp_att_list = []
file_name_list = os.listdir(folder_path)

#code to extract nearest waypoint files
for file_name in file_name_list:
    file_path = os.path.join(folder_path, file_name)
    if os.path.isfile(file_path):
        with open(file_name) as f:
            for i, line in enumerate(f):
                if i == 0:
                    if not line.startswith('QGC WPL 110'):
                        raise Exception('File is not supported WP version')
                elif i ==1:
                    linearray = line.split('\t')
                    ln_x = np.uint32(linearray[8])
                    ln_y = np.uint32(linearray[9])
                    ln_z = float(linearray[10])
                    wpf_dis_list.append(math.sqrt((ln_x-curr_lat)**2+(ln_y-curr_lon)**2))
                    break
    print(file_path)
min_dis = min(wpf_dis_list)
for i,j in wpf_dis_list:
     if min_dis==j:
          near_index = i
          break
Final_wpf = file_name_list[near_index]

#a command function to set home location
def cmd_set_home(home_location, altitude):
    print('--- ', the_connection.target_system, ',', the_connection.target_component)
    the_connection.mav.command_long_send(
        the_connection.target_system, the_connection.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_HOME,
        1,  # set position
        0,  # param1
        0,  # param2
        0,  # param3
        0,  # param4
        home_location[0],  # lat
        home_location[1],  # lon
        altitude)

#function to upload mission to planner
def uploadmission(aFileName):
    home_location = [curr_lat,curr_lon]
    home_altitude = None

    with open(aFileName) as f:
        for i, line in enumerate(f): #i iterates as normal int and line iterates every line in the file
            if i == 0: 
                #to check that waypoint is that or not
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                #split all the words in the line
                linearray = line.split('\t')
                #assigning every param to a variable
                ln_seq = int(linearray[0])
                ln_current = int(linearray[1])
                ln_frame = int(linearray[2])
                ln_command = int(linearray[3])
                ln_param1 = float(linearray[4])
                ln_param2 = float(linearray[5])
                ln_param3 = float(linearray[6])
                ln_param4 = float(linearray[7])
                ln_x = np.uint32(linearray[8])
                ln_y = np.uint32(linearray[9])
                ln_z = float(linearray[10])
                ln_autocontinue = float(linearray[11].strip())
                if (i == 1):
                    #home_location = (ln_x, ln_y)
                    home_altitude = ln_z
                p = mavutil.mavlink.MAVLink_mission_item_message(the_connection.target_system, the_connection.target_component, ln_seq,
                                                                 ln_frame,
                                                                 ln_command,
                                                                 ln_current, ln_autocontinue, ln_param1, ln_param2,
                                                                 ln_param3, ln_param4, ln_x, ln_y, ln_z)
                wp.add(p)

    cmd_set_home(home_location, home_altitude)
    #to read Command acknowledge from receive packets
    msg = the_connection.recv_match(type=['COMMAND_ACK'], blocking=True)
    #to print the recieved cmd acknowledge and set home location
    print(msg)
    print('Set home location: {0} {1}'.format(home_location[0], home_location[1]))
    time.sleep(1)

    # send waypoint to airframe
    the_connection.waypoint_clear_all_send()
    the_connection.waypoint_count_send(wp.count())

    for i in range(wp.count()):
        msg = the_connection.recv_match(type=['MISSION_REQUEST'], blocking=True)
        print(msg)
        the_connection.mav.send(wp.wp(msg.seq))
        print('Sending waypoint {0}'.format(msg.seq))

uploadmission('Final_wpf')
   