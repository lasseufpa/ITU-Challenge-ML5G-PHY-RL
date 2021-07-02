'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Takashi, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script to train the baseline of reinforcement learning applied to Beam-selection
V1.0
'''

import sys
import csv
import numpy as np
import pandas as pd
from beamselect_env import BeamSelectionEnv
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines import A2C

# Creat the folder
try:
    os.mkdir('./model')
except OSError as error:
    print(error)

'''
Trains an A2C network and stores it in a file.
'''
train_ep = 0
e = BeamSelectionEnv(ep=train_ep)

model = A2C(policy="MlpPolicy", 
            learning_rate=1e-3, 
            n_steps=1, 
            verbose=1,
            gamma=0.7, 
            env=e, 
            seed=0,
            tensorboard_log="./log_tensorboard/")

# model.learn(total_timesteps=800000)
model.learn(total_timesteps=1000)
model_file_name = "./model/"+str(sys.argv[1])+".a2c" 
model.save(model_file_name)