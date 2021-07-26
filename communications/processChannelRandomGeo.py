#Script context use	: This script is for CAVIAR purposes uses
#Author       		: Ailton Oliveira
#Email          	: ailton.pinto@itec.ufpa.br

import numpy as np
from .mimo_channels import getNarrowBandULAMIMOChannel, getNarrowBandUPAMIMOChannel
import scipy.constants as sc

##################################
### Script configuration
##################################

def friis_propagation(Ptx, R, freq, gain=5):
    h = sc.c / freq
    #gain and effectiver aperture default for isotropic ideal antenna
    Prx = (20*np.log10((h/(4*np.pi*R)**2))+Ptx+gain)
    return Prx

def ULAChannelRandomGeo(data, frequency = 60e6,spread = 0.5, Nr= 1, Nt = 64):
    #seed = 75648
    #np.random.seed(seed)  
    numRays = 2
    freq =frequency
    Ptx = 90 #(db)
    angle_spread = spread
    departure = data[0]
    arrival = data[1]
    distance = data[4]

    gain = abs(np.random.randn(numRays)) + abs(np.random.randn(numRays))
    #gain_in_dB = 20*np.log10(np.abs(gain))  
    gain_in_dB = friis_propagation(Ptx, distance, freq, gain=gain+25)
    AoD_az = departure + angle_spread*np.random.randn(numRays)
    AoA_az = arrival + angle_spread*np.random.randn(numRays)
    phase = np.angle(gain)*180/np.pi
        
    Ht = getNarrowBandULAMIMOChannel(AoD_az, AoA_az, gain_in_dB, Nt, Nr, pathPhases=phase) 
    #Ht = Ht / np.linalg.norm(Ht) #normalize channel to unit norm

    return Ht

def UPAChannelRandomGeo(data, frequency = 60e6,spread = 1, Nr= 1, Nt = 64):
    #seed = 75648
    #np.random.seed(seed)  
    numRays = 2
    freq =frequency
    Ptx = 99 #(db)
    angle_spread = spread
    departure_az = data[0]
    arrival_az = data[1]
    departure_el = data[2]
    arrival_el = data[3]
    distance = data[4]

    gain = abs(np.random.randn(numRays)) + abs(np.random.randn(numRays))
    #gain_in_dB = 20*np.log10(np.abs(gain))  
    gain_in_dB = friis_propagation(Ptx, distance, freq, gain=gain+25)
    AoD_az = departure_az + angle_spread*np.random.randn(numRays)
    AoD_el = departure_el + angle_spread*np.random.randn(numRays)
    AoA_az = arrival_az + angle_spread*np.random.randn(numRays)
    AoA_el = arrival_el + angle_spread*np.random.randn(numRays)
    phase = np.angle(gain)*180/np.pi
    
    UPA_side = int(np.sqrt(Nt))
        
    Ht = getNarrowBandUPAMIMOChannel(AoD_el,AoD_az,AoA_el, AoA_az,gain_in_dB,UPA_side,UPA_side,Nr,Nr,pathPhases=phase) 

    return Ht

