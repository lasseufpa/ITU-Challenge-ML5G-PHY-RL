'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Enviroment for reinforcement learning applied to Beam-selection
V1.0
'''

import numpy as np
from gym import Env
from gym.spaces import Box, MultiDiscrete

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
        self.caviar_bs = BaseStation(Elements=64, frequency=60e9,name='BS1',ep_lenght=20, traffic_type = 'dense', BS_type = 'UPA', change_type=True)

        #Append users
        self.caviar_bs.append(self.ue1)
        self.caviar_bs.append(self.ue2)
        self.caviar_bs.append(self.ue3)
        
        '''
        The observation space is composed by an array with 7 float numbers. 
        The first three represent the user position in XYZ, while the 
        remaining ones are respectively: dropped packages, sent packages, 
        buffered and bit rate.
        '''
        self.observation_space = Box(
            low=np.array([-5e2,-5e2,-5e2,0,0,0,0]), 
            high=np.array([5e2,5e2,5e2,1e3,1e3,2e4,1e9]),
            shape=(7,)
    )
        '''
        The action space is composed by an array with two integers. The first one 
        represents the user that is currently being allocated and the second one, 
        the codebook index.
        '''
        self.action_space = MultiDiscrete([len(self.caviar_bs.UEs), self.caviar_bs._NTx])
        
        self.reset()


    def reset(self):
        self._state = np.zeros(7)
        return self._state
    
    '''
    The step function receives a user and the beam index to serve it. The user state 
    is updated at every step by checking the correspondent element inside the simulator.
     
    :param action: (array) is composed by the user ID and the codebook index
    '''
    def step(self, action):
        target, index = action
        bs_example_state, bs_example_reward, info, done = self.caviar_bs.step(target,index)
        self.state = bs_example_state
        reward = bs_example_reward
        return self.state, reward, done, info
    
    def best_beam_step(self, target):
        bs_example_state, bs_example_reward, info, done = self.caviar_bs.best_beam_step(target)
        self.state = bs_example_state
        reward = bs_example_reward
        return self.state, reward, done, info