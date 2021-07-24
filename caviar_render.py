'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script to render UE4 simulations after beam selection
V0.1
'''

import caviar_config
import caviar_tools
import airsim
import math
import csv
import time
import os
import cv2
import tqdm
import random
import numpy as np

simulation_torender_path = './episodes/ep0.csv'
rl_out_path = './data/data_output_test9.a2c.csv'
best_beam_out_path = './data/data_best_Beams_test9.a2c.csv'

# Create a folder to write the output videos
try:
    os.mkdir('./render_out')
except OSError as error:
    print(error)


client = caviar_tools.airsim_connect()

# Create the output video
# The video resolution can be defined at airsim settings file
rawimg = caviar_tools.airsim_getimages(client, caviar_config.drone_ids[0])
img = cv2.imdecode(airsim.string_to_uint8_array(rawimg), cv2.IMREAD_COLOR)
out = cv2.VideoWriter('./render_out/outp4.avi',
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         50, (img.shape[1],img.shape[0]))

Nt = 64
Wt = caviar_tools.dft_codebook(Nt) / np.sqrt(Nt) # DFT Codebook
#exit(-1)

#angles_beam = caviar_tools.get_ula_beamangles(Wt, Nt, 32)


# Read simulation file
obj_list = []
with open(simulation_torender_path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_reader.__next__()
    for row in csv_reader:
        obj_pose = [float(row[2]), float(row[3]), float(row[4])]
        obj_orientation = [float(row[5]), float(row[6]), float(row[7]), float(row[8])]
        obj_out = [row[1],obj_pose, obj_orientation]
        obj_list.append(obj_out)

rl_beam_index = []
with open(rl_out_path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_reader.__next__()
    for row in csv_reader:
        beam_index = [row[0], int(row[2])]
        rl_beam_index.append(beam_index)

best_beam_index = []
with open(rl_out_path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_reader.__next__()
    for row in csv_reader:
        beam_index = [row[0], int(row[2])]
        best_beam_index.append(beam_index)

caviar_tools.airsim_takeoff_all(client)

# Chose the UAV camera position and orientation, the video will be recorded using this camera
camera_pose = airsim.Pose(airsim.Vector3r(-8, 0, -5), airsim.to_quaternion(math.radians(-20), 0, 0)) #radians
client.simSetCameraPose("0", camera_pose)

# Simulation rendering process
print('Start rendering...')
beam_index_to_plot = 0
for obj in tqdm.tqdm(obj_list[::2]):

    #check if it's a uav or other object
    if 'uav' in obj[0]:
        caviar_tools.airsim_setpose_offset(client, obj[0],obj[1][0], obj[1][1], obj[1][2], obj[2][0], obj[2][1], obj[2][2], obj[2][3])
        time.sleep(0.1)
        if rl_beam_index[beam_index_to_plot][1] == best_beam_index[beam_index_to_plot][1]:
            angles_beam = caviar_tools.get_ula_beamangles(Wt, Nt, rl_beam_index[beam_index_to_plot][1])
            print(angles_beam)
            caviar_tools.unreal_plotbeam(client, 3000, angles_beam, 0, 0.1)
        else:
            angles_beam = caviar_tools.get_ula_beamangles(Wt, Nt, rl_beam_index[beam_index_to_plot][1])
            caviar_tools.unreal_plotbeam(client, 3500, angles_beam, 0, 0.15)
            angles_beam = caviar_tools.get_ula_beamangles(Wt, Nt, best_beam_index[beam_index_to_plot][1])
            caviar_tools.unreal_plotbeam_best(client, 3000, angles_beam, 0, 0.1)

        caviar_tools.unreal_plotbox(client, rl_beam_index[beam_index_to_plot][0], 0.1)
        client.simPause(True)
        rawimg = caviar_tools.airsim_getimages(client, caviar_config.drone_ids[0])
        img = cv2.imdecode(airsim.string_to_uint8_array(rawimg), cv2.IMREAD_COLOR)
        out.write(img)
        beam_index_to_plot += 2
        client.simPause(False)
    else:
        caviar_tools.unreal_setpose(client, obj[0],obj[1][0], obj[1][1], obj[1][2], obj[2][0], obj[2][1], obj[2][2], obj[2][3])

out.release()
print('Done')
