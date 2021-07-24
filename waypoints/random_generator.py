'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git
'''

'''
Script to generate random trajectories for AirSim UAVs
V1.0
'''

import csv
import time
import os
import random
from copy import deepcopy

n_trajectories = 500

def shuffle_weight():
  return random.random()

try:
    os.mkdir('./trajectories')
except OSError as error:
    print(error)

path_list1 = []
with open('./q1.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_reader.__next__()

    for row in csv_reader:
        path_list1.append(row)

path_list2 = []
with open('./q2.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_reader.__next__()

    for row in csv_reader:
        path_list2.append(row)

path_list3 = []
with open('./q3.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_reader.__next__()

    for row in csv_reader:
        path_list3.append(row)

path_list4 = []
with open('./q4.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_reader.__next__()

    for row in csv_reader:
        path_list4.append(row)

land_points = []
with open('./land_points.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_reader.__next__()

    for row in csv_reader:
        land_points.append(row)

for i in range(n_trajectories):
    path = []

    list1 = deepcopy(path_list1)
    list2 = deepcopy(path_list2)
    list3 = deepcopy(path_list3)
    list4 = deepcopy(path_list4)
    listl = deepcopy(land_points)

    random.shuffle(list1, shuffle_weight)
    random.shuffle(list2, shuffle_weight)
    random.shuffle(list3, shuffle_weight)
    random.shuffle(list4, shuffle_weight)
    random.shuffle(listl, shuffle_weight)

    path.extend(random.sample(list1, 1))
    path.extend(random.sample(list2, 1))
    path.extend(random.sample(list3, 1))
    path.extend(random.sample(list4, 1))

    random.shuffle(path, shuffle_weight)

    for j in path:
        j[2] = random.randint((int(j[2])-4),int(j[2]))

    path.insert(0,['0','0','-22'])

    landp = random.sample(listl, 1)[0]
    path.append([landp[0],landp[1],landp[2]])
    path.append([landp[0],landp[1],'-0.5'])

    with open('./trajectories/path' + str(i) + '.csv', mode='w', newline='') as csv_file:

        fieldnames = ['x', 'y', 'z']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for k in path:
            writer.writerow({'x': k[0], 'y': k[1], 'z': k[2]})
