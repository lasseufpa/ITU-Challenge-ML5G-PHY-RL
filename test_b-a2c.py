'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script to test baseline agent
V1.0
'''

import os
import sys
import csv
import argparse
import numpy as np
import pandas as pd
import os
import caviar_tools
from beamselect_env import BeamSelectionEnv
from stable_baselines import A2C


# Create the folder
try:
    os.mkdir('./data')
except OSError as error:
    print(error)

'''
Tests an A2C network previously trained and stored in file.
'''
def test_beam_selection(model_path, model_name, test_ep, full_output):
    # Set the range of episodes the agent will work on
    if len(test_ep) >= 2:
        test_ep = range(int(test_ep[0]), int(test_ep[1])+1)
    
    for ep in test_ep:
        # Get total number of steps based on the timestamps for a specific UE
        n_steps = caviar_tools.linecount([ep])
        env = BeamSelectionEnv(ep=[ep])
        model = A2C.load(model_path)
        obs = env.reset()
        if full_output == True:
            output_file = './data/'+'output_'+model_name+'_ep'+str(ep)+'.csv'
            with open(output_file, 'w', newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                ['chosen_ue']+
                ['ue_index']+
                ['beam_index']+
                ['x']+
                ['y']+
                ['z']+
                ['pkts_dropped']+
                ['pkts_transmitted']+
                ['pkts_buffered']+
                ['bit_rate_gbps']+
                ['channel_mag']+
                ['reward'])
                for i in range(n_steps):
                    action, _states = model.predict(obs)
                    obs, reward, done, info = env.step(action)
                    writer.writerow(
                        [info['chosen_ue']]+
                        [action[0]]+
                        [action[1]]+
                        [obs[0]]+
                        [obs[1]]+
                        [obs[2]]+
                        [info['pkts_dropped']]+
                        [info['pkts_transmitted']]+
                        [info['pkts_buffered']]+
                        [info['bit_rate']/1e+9]+
                        [info['channel_mag']]+
                        [float(reward)])
        else:
            output_file = './data/'+'actions_'+model_name+'_ep'+str(ep)+'.csv'
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['chosen_ue']+
                                ['ue_index']+
                                ['beam_index'])
                for i in range(n_steps):
                    action, _states = model.predict(obs) 
                    obs, reward, done, info = env.step(action)
                    writer.writerow([info['chosen_ue']]+
                                    [action[0]]+
                                    [action[1]])
                
        # Free memory
        del model, env

'''
Usage:

$ python3 test_b-a2c.py -m <model_name> -ep <test_ep_id#first> <test_ep_id#last> --full-output <if not then only actions>

Example:

$ python3 test_b-a2c.py -m baseline.a2c -ep 0 1 --full-output
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
                         "last episodes to test",
                    action="store", 
                    dest="episode", 
                    type=str)

parser.add_argument("--full-output", "-f",
                    help="If activated yields all info " +
                           "regarding the agent performance " +
                           "in each step, if not, only actions",
                    action="store_true", 
                    dest="full_output")

args = parser.parse_args()

model_path = "./model/"+str(args.model)
# Take out the file format and save only the model name
model_name = args.model.partition('.')[0]

test_beam_selection(model_path=model_path,
                    model_name=model_name, test_ep=args.episode, 
                    full_output=args.full_output)