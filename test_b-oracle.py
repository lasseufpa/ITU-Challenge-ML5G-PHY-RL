'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git

Script to create BeamOracle agent for baseline
V1.0
'''

import os
import csv
import argparse
import caviar_tools
from beamselect_env import BeamSelectionEnv


# Create the folder
try:
    os.mkdir('./data/beamoracle')
except OSError as error:
    print(error)

'''
Creates a BeamOracle agent and saves the output in a file
'''
def beam_oracle(test_ep, full_output, dummy_type='random'):
    # Set the range of episodes that dummy will work on
    if len(test_ep) >= 2:
        test_ep = range(test_ep[0], test_ep[1]+1)
    
    for ep in test_ep:
        # Get total number of steps based on the timestamps for a specific UE
        n_steps = caviar_tools.linecount([ep])
        env = BeamSelectionEnv(ep=[ep])
        if full_output == True:
            output_file = './data/beamoracle/'+'output_b_beam_oracle_ep'+ str(ep)+ '.csv'
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
                    action = user(i)
                    obs, reward, done, info = env.best_beam_step(action)
                    writer.writerow(
                        [info['chosen_ue']]+
                        [action]+
                        [info['best_beam']]+
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
            output_file = './data/beamoracle/'+'actions_b_beam_oracle_ep'+ str(ep)+ '.csv'
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['chosen_ue']+
                                ['ue_number']+
                                ['beam_index'])
                for i in range(n_steps):
                    action = user(i)
                    obs, reward, done, info = env.best_beam_step(action)
                    writer.writerow([info['chosen_ue']]+
                                    [action]+
                                    [info['best_beam']])
                
        # Free memory
        del env

def user(step):
    # 3 is the total number of users
    # user is chosen with the following pattern 0,1,2,0...
    user = step % 3
    return user


'''
Usage:

$ python3 test_b-oracle.py -ep <test_ep_id#1> <test_ep_id#n> --full-output <if not then only actions>

Example:

$ python3 test_b-oracle.py -ep 0 1 --full-output 
'''

parser = argparse.ArgumentParser()

parser.add_argument("--episode", "-ep",
                    nargs='+',
                    help="ID of the episodes to test", 
                    action="store", 
                    dest="episode", 
                    type=int)

parser.add_argument("--full-output", "-f",
                    help="If activated yields all info " +
                           "regarding the agent performance " +
                           "in each step, if not, only actions",
                    action="store_true", 
                    dest="full_output")

args = parser.parse_args()

beam_oracle(test_ep=args.episode, 
            full_output=args.full_output)