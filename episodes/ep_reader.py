#Script context use	: This script is for CAVIAR purposes uses
#Author       		: Rebecca Aben-Athar
#Email          	: rebecca.athar@itec.ufpa.br 

import numpy as np
import csv
import sys

if len(sys.argv) < 2: 
    print('insufficient arguments')
    print('Expected python3 test_ep_reader.py Episode_ID Users_list')
    print('Try: python3 ep_reader.py 0 uav1,simulation_car1,simulation_pedestrian1')
    sys.exit()

episode = sys.argv[1]
users = sys.argv[2].split(",")


with open('./ep{}.csv'.format(0)) as read_file: #Input file
    with open('./users_ep{}.csv'.format(0), 'w') as write_file: #Output file
        episode_data = csv.DictReader(read_file)
        output_data = csv.writer(write_file)
        write_header = True
        print('writing...')
        for row in episode_data:
            if write_header:
                headers = list(row.keys())
                output_data.writerow(headers)
                write_header = False
            if row['obj'] in users:
                values = row.values()
                values = list(values)
                output_data.writerow(values)
            




