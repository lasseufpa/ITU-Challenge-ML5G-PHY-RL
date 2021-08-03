'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script to train the baseline of reinforcement learning applied to Beam-selection
V1.0
'''

import os
import sys
import csv
import argparse
import numpy as np
import pandas as pd
import caviar_tools
from beamselect_env import BeamSelectionEnv
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines import A2C


# Create the folder
try:
    os.mkdir('./model')
except OSError as error:
    print(error)

'''
Trains an A2C network and stores it in a file.

Usage:

$ python3 train_b-a2c.py -m <model_name> -ep <train_ep_id#first> <train_ep_id#last>

Example:

$ python3 train_b-a2c.py -m baseline.a2c -ep 0 1
'''
parser = argparse.ArgumentParser()

parser.add_argument("--model", "-m", 
                    help="Pass RL model name",
                    action="store", 
                    dest="model", 
                    type=str)

parser.add_argument("--episode", "-ep",
                    nargs='+',
                    help="IDs of the first and " +
                         "last episodes to train", 
                    action="store", 
                    dest="episode", 
                    type=str)
                   
args = parser.parse_args()

e = BeamSelectionEnv(ep=args.episode)

# Get total number of steps based on the timestamps for a specific UE  
n_steps = caviar_tools.linecount(args.episode)

model = A2C(policy="MlpPolicy", 
            learning_rate=1e-3, 
            n_steps=1, 
            verbose=1,
            gamma=0.7, 
            env=e, 
            seed=0,
            tensorboard_log="./log_tensorboard/")

model.learn(total_timesteps=n_steps)
model_path = "./model/"+str(args.model)
model.save(model_path) 