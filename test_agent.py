'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Takashi, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script to test baseline agent
V1.0
'''
import sys
import os
import csv
import numpy as np
import pandas as pd
from beamselect_env import BeamSelectionEnv
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines import A2C


# Creat the folder
try:
    os.mkdir('./data')
except OSError as error:
    print(error)

'''
Tests an A2C network previously trained and stored in file.
'''
def test_beam_selection(model_file_name, model_name, test_ep):
    env = BeamSelectionEnv(ep=test_ep) 
    model = A2C.load(model_file_name)
    obs = env.reset()
    output_file = './data/'+'actions_'+model_name+'.csv'
    with open(output_file, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user']+['beam_index'])
        # 5325 is the amount of time steps in the dataset
        for i in range(5325):
            action, _states = model.predict(obs) 
            obs, reward, dones, info = env.step(action)
            writer.writerow([action[0]]+[action[1]])
            
    # Free memory
    del model, env

'''
Usage:

$ python3 test_agent.py "model_name" "test_ep_id"

Example:

$ python3 test_agent.py test 1
'''

model_name = str(sys.argv[1])
model_file_name = "./model/"+str(sys.argv[1])+".a2c"
test_ep = [sys.argv[2]]
#test_ep = sys.argv[2]
test_beam_selection(model_file_name, model_name, test_ep)