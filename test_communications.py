'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Takashi, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script to test telecommunications dynamics/environment
V1.0
'''

import numpy as np
from communications.buffer import Buffer
from communications.base_station import BaseStation
from communications.ue import UE

use_airsim = False
obj_type = 'UAV'

# Test integration
print('/////////////// Test integration ///////////////')
episode = [0,1]
#episode = [0]
ue1 = UE(name='uav1', obj_type=obj_type, total_number_rbs=17, episode=episode, use_airsim=use_airsim)
ue2 = UE(name='simulation_car1', obj_type=obj_type, total_number_rbs=17, episode=episode, use_airsim=use_airsim)
ue3 = UE(name='simulation_pedestrian1', obj_type=obj_type, total_number_rbs=17, episode=episode, use_airsim=use_airsim)
caviar_bs = BaseStation(Elements=64, frequency=60e9,name='BS1',ep_lenght=20, traffic_type='light', BS_type = 'UPA')
#Append users
caviar_bs.append(ue1)
caviar_bs.append(ue2)
caviar_bs.append(ue3)

user = -1
action = 32

for i in range(20):
	if user == 2:
		user = -1
	user += 1
	state, reward, feedback ,done = caviar_bs.step(user,action)
	print('User ID: ', caviar_bs.UEs[user].ID, 'Buffer: ', caviar_bs.UEs[user].buffer, 'BS TYPE: ', caviar_bs._type)
	print('###')

