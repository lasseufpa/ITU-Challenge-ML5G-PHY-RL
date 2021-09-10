#Script context use	: This script is for CAVIAR purposes uses
#Author       		: Ailton Oliveira
#Email          	: ailton.pinto@itec.ufpa.br

import os
from .processChannelRandomGeo import ULAChannelRandomGeo, UPAChannelRandomGeo
import numpy as np

def cart2pol(x, y, z):
   #Adjust angular domain to X-axis
    if x == 0:
       x += 0.001
    rho = np.sqrt(x**2 + y**2 + z**2)
    phi = np.rad2deg(np.arctan2(y, x))
    if phi < 0:
       phi +=  360
    elev = np.rad2deg(np.arccos(z/rho))
    return(elev, phi)

def drone_info(UE = [5,4,3], Bs = [0, 0, 0]):
   #Convert to polar domain Bs = [-15, 30, -1]
   droneRho, dronePhi = cart2pol(Bs[0]-UE[0],Bs[1]-UE[1], Bs[2]-UE[2])
   #print('Position:', UE[0], UE[1], UE[2])
   bsRho, bsPhi = cart2pol(UE[0]-Bs[0],UE[1]-Bs[1], UE[2]-Bs[2])
   #print('Angles: Elevation ', bsRho, ', Azhimutal ' ,bsPhi)
   distance = np.sqrt(((UE[0]-Bs[0])**2)+((UE[1]-Bs[1])**2)+((UE[2]-Bs[2])**2))
   return [bsPhi,dronePhi, bsRho, droneRho, distance]

def ULA_best_beam(H, codebook):
   codebook_tx = codebook
   EquivalentChannels = np.dot(np.squeeze(np.asarray(H)), codebook_tx)
   bestIndex = np.argmax(np.abs(EquivalentChannels))
   return bestIndex

def ULAchannel(position,frequency=60e9,Nt=64, Nr=1):
   drone_data = drone_info(UE = list(position))
   # Calculate de H for all codebook, and return the index of the best beam
   Ht = ULAChannelRandomGeo(data=drone_data, frequency=frequency,spread=1,Nr = Nr, Nt = Nt)
   return Ht

def UPAchannel(position,frequency=60e9,Nt=64, Nr=1):
   drone_data = drone_info(UE = list(position))
   # Calculate de H for all codebook, and return the index of the best beam
   Ht = UPAChannelRandomGeo(data=drone_data, frequency=frequency,spread=1,Nr = Nr, Nt = Nt)
   return Ht

def chosen_precoder(index, H, Txcodebook):
   codebook_tx = Txcodebook
   EquivalentChannels = np.dot(np.squeeze(np.asarray(H)), codebook_tx[:, index])
   #EquivalentChannels = np.dot(np.squeeze(np.asarray(H)), codebook_tx)
   return np.squeeze(np.abs(EquivalentChannels))



