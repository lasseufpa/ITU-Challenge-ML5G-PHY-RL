'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Takashi, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script for demonstration flight with Airsim
V1.0
'''

import caviar_config
import caviar_tools
import csv
import time
import os

n_trajectories = 200

client = caviar_tools.airsim_connect()

for episode in range(n_trajectories):
    print('Episode: ' + str(episode))
    not_landed = True
    takeoff_complete = False
    caviar_tools.airsim_reset(client)
    caviar_tools.airsim_takeoff_all(client)

    caviar_tools.move_on_path(client, caviar_config.drone_ids[0], './paths/trajectories/path' + str(episode ) + '.csv')

    while(not_landed):

        uavs_pose = caviar_tools.airsim_getpose(client, caviar_config.drone_ids[0])

        if takeoff_complete:
            if (uavs_pose[2] >= -0.8):
                not_landed = False
        else:
            if (uavs_pose[2] <= -5):
                takeoff_complete = True
