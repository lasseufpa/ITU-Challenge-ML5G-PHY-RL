'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Takashi, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Enviroment for reinforcement learning applied to Beam-selection
V1.0
'''

import numpy as np
import pandas as pd
from gym import Env
from gym.spaces import Box, MultiDiscrete
from random import randrange

from communications.buffer import Buffer
from communications.base_station import BaseStation
from communications.ue import UE

class BeamSelectionEnv(Env):
    def __init__(self, ep=[0]):
        # Which episode to take data from (Only used when use_airsim=False).
        self.eps = ep
        '''
        Defining simulation environment with one BS and three UEs
        '''
        self.ue1 = UE(name='uav1', obj_type='UAV', total_number_rbs=15, episode = self.eps, use_airsim=False)
        self.ue2 = UE(name='simulation_car1', obj_type='CAR', total_number_rbs=15, episode = self.eps, use_airsim=False)
        self.ue3 = UE(name='simulation_pedestrian1', obj_type='PED', total_number_rbs=15, episode = self.eps, use_airsim=False)
        self.caviar_bs = BaseStation(Elements=64, frequency=60e9,name='BS1',ep_lenght=20)
        #Append users
        self.caviar_bs.append(self.ue1)
        self.caviar_bs.append(self.ue2)
        self.caviar_bs.append(self.ue3)
        
        '''
        The observation space is composed by an array with 6 float numbers. 
        The first three represent the user position in XYZ, while the 
        remaining ones are respectively: dropped packages, sent packages 
        and bit rate.
        '''        
        self.observation_space = Box(
            low=np.array([-5e2,-5e2,-5e2,0,0,0]), 
            high=np.array([5e2,5e2,5e2,1e3,1e3,1e9]),
            shape=(6,)
    )
        '''
        The action space is composed by an array with two integers. The first one 
        represents the user that is currently being allocated and the second one, 
        the codebook index.
        '''
        self.action_space = MultiDiscrete([len(self.caviar_bs.UEs), self.caviar_bs._NTx])
        
        self.reset()


    def reset(self):
        self._state = np.zeros(6)
        return self._state
    
    '''
    The step function receives a user and the beam index to serve it. The user state 
    is updated at every step by checking the correspondent element inside the simulator.
     
    :param action: (array) is composed by the user ID and the codebook index
    '''
    def step(self, action):
        target, index = action
        state, reward, feedback, done = self.caviar_bs.step(target,index)
        dict_keys = ['x', 'y', 'z', 'dropped_packets', 'sent_packets', 'bit_rate']
        feedback = dict(zip(dict_keys, feedback))
        self.state = state
        return self.state, np.array(reward), done, feedback