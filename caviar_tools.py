'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git


Auxiliary methods for CAVIAR simulations
V1.0
'''

import caviar_config
from communications.mimo_channels import arrayFactorGivenAngleForULA
import airsim
import csv
import time
import os
import sys
import pandas as pd
import numpy as np
from communications.UPA_class import UPA
import matplotlib.pyplot as plt

def airsim_connect():
    client = airsim.MultirotorClient()
    client.confirmConnection()
    return client

def airsim_takeoff(client, uav_id):
    client.enableApiControl(True, uav_id)
    client.armDisarm(True, uav_id)
    client.takeoffAsync(vehicle_name=uav_id).join()

def airsim_takeoff_all(client):
    for uav in caviar_config.drone_ids:
        airsim_takeoff(client, uav)

def airsim_reset(client):
    client.reset()

def airsim_land(client, uav_id):
    landed = client.getMultirotorState(vehicle_name=uav_id).landed_state
    #Ailton OBS: Check if this if works
    if landed == airsim.LandedState.Landed:
        print("already landed...")
    else:
        client.armDisarm(False, uav_id)
    client.enableApiControl(False, uav_id)

def airsim_land_all(client):
    for uav in caviar_config.drone_ids:
        airsim_land(client, uav)

def move_on_path(client, uav, path, speed = 5):

    path_list = []

    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        csv_reader.__next__()

        for row in csv_reader:
            path_list.append(airsim.Vector3r(float(row[0]), float(row[1]), float(row[2])))

    client.enableApiControl(True, uav)
    client.moveOnPathAsync(path_list, speed,3e+38, airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False,0), vehicle_name=uav)

def UPA_DFT_angles(Nx, Ny, user_angle):
    user_azhi, user_elev = user_angle
    UPA(Nx, Ny)
    array_factor_UPA = UPA.ArrayFactorUPA()
    azhimut, elevat = UPA.get_angles()
    Roffset = 0.5 # Offset to define the radiation peak
    azhimutal = []
    elevation = []
    maxR = np.amax(abs(array_factor_UPA[indX,:,:]))
    indices = np.where((abs(array_factor_UPA[indX,:,:])<maxR + Roffset) & (abs(array_factor_UPA[indX,:,:])>maxR - Roffset))
    for ind_az in list(indices[0]):
        angles = np.rad2deg(azhimut[ind_az])
        azhimutal.append(float(angles))
    for ind_elev in list(indices[1]):
        angles = np.rad2deg(elevat[ind_elev])
        elevation.append(float(angles))
    #TO-DO filter de angle closest to the angle target
    print("UPA Angles:")
    azhimutal.sort()
    #print(azhimutal)
    print('######')
    elevation.sort()
    #print(elevation)

def info_csv(user_id,episode):
    with open('./episodes/ep{}.csv'.format(episode)) as cs:
        episode_data = csv.DictReader(cs)
        info=[]
        for row in episode_data:
            if row['obj'] == user_id:
                values = list(row.values())
                tmp_info = str(",".join(values))
                info.append(tmp_info)
    return iter(info)


def positions_csv(user_id,episode):
    with open('./episodes/ep{}.csv'.format(episode)) as cs:
        episode_data = csv.DictReader(cs)
        output = []
        for row in episode_data:
            if row['obj'] == user_id:
                xyz = ('{},{},{}').format(row['pos_x'], row['pos_y'], row['pos_z'])
                output.append(xyz)
    return iter(output)

def move_to_point(client, uav, x, y, z, speed = 5):
    client.enableApiControl(True)
    client.moveToPositionAsync(x, y, z, speed, 3e+38, airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False,0), vehicle_name=uav)

def airsim_getpose(client,uav_id):
    coordinates =  client.getMultirotorState(vehicle_name=uav_id).kinematics_estimated.position.to_numpy_array()
    return coordinates

def airsim_getpose_offset(client,uav_id):
    coordinates =  client.getMultirotorState(vehicle_name=uav_id).kinematics_estimated.position.to_numpy_array()
    coordinates_offset = np.add(coordinates, caviar_config.initial_pose_offset)
    return coordinates_offset

def airsim_getorientation(client,uav_id):
    orientation =  client.getMultirotorState(vehicle_name=uav_id).kinematics_estimated.orientation.to_numpy_array()
    return orientation

def airsim_getangularacc(client,uav_id):
    acc =  client.getMultirotorState(vehicle_name=uav_id).kinematics_estimated.angular_acceleration.to_numpy_array()
    return acc

def airsim_getangularvel(client,uav_id):
    vel =  client.getMultirotorState(vehicle_name=uav_id).kinematics_estimated.angular_velocity.to_numpy_array()
    return vel

def airsim_getlinearacc(client,uav_id):
    acc =  client.getMultirotorState(vehicle_name=uav_id).kinematics_estimated.linear_acceleration.to_numpy_array()
    return acc

def airsim_getlinearvel(client,uav_id):
    vel =  client.getMultirotorState(vehicle_name=uav_id).kinematics_estimated.linear_velocity.to_numpy_array()
    return vel

def airsim_gettimestamp(client,uav_id):
    timestamp =  client.getMultirotorState(vehicle_name=uav_id).timestamp
    return timestamp

def airsim_getcollision(client,uav_id):
    collision =  client.getMultirotorState(vehicle_name=uav_id).collision.has_collided
    return collision

def airsim_setpose(client, uav_id, x, y, z, orien_x, orien_y, orien_z, orien_w):
    success = client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(x, y, z),airsim.Quaternionr(x_val = orien_x, y_val = orien_y, z_val = orien_z, w_val = orien_w)),True,vehicle_name = uav_id)
    return success

def airsim_setpose_offset(client, uav_id, x, y, z, orien_x, orien_y, orien_z, orien_w):
    x = x - caviar_config.initial_pose_offset[0]
    y = y - caviar_config.initial_pose_offset[1]
    z = z - caviar_config.initial_pose_offset[2]
    success = client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(x, y, z),airsim.Quaternionr(x_val = orien_x, y_val = orien_y, z_val = orien_z, w_val = orien_w)),True,vehicle_name = uav_id)
    return success

def unreal_getpose(client, obj_id):
    coordinates =  client.simGetObjectPose(obj_id).position.to_numpy_array()
    return coordinates

def unreal_getorientation(client, obj_id):
    orientation =  client.simGetObjectPose(obj_id).orientation.to_numpy_array()
    return orientation

def unreal_setpose(client, obj_id,x, y, z, orien_x, orien_y, orien_z, orien_w):
    success = client.simSetObjectPose(obj_id, airsim.Pose(airsim.Vector3r(x, y, z), airsim.Quaternionr(x_val = orien_x, y_val = orien_y, z_val = orien_z, w_val = orien_w)), True)
    return success

def unreal_plotbeam(client, distance, azimuth, elevation, duration):
    success = client.simRunConsoleCommand('ke caviar_base_station plot_beam ' + str(distance) + ' ' + str(azimuth) + ' ' + str(elevation) + ' ' + str(duration) + ' (R=0.9, G=0.45, B=0.0, A=1.0)')
    return success

def unreal_plotbeam_best(client, distance, azimuth, elevation, duration):
    success = client.simRunConsoleCommand('ke caviar_base_station plot_beam ' + str(distance) + ' ' + str(azimuth) + ' ' + str(elevation) + ' ' + str(duration) + ' (R=0.26, G=0.52, B=0.96, A=1.0)')
    return success

def unreal_plotbox(client, actor, duration):
    success = client.simRunConsoleCommand('ke caviar_base_station plot_box ' + str(actor) + ' ' + str(duration))
    return success

def airsim_save_images(client, record_path = './'):
    for uav in caviar_config.drone_ids:
        png_image = client.simGetImage("0", airsim.ImageType.Scene,  vehicle_name=uav)
        airsim.write_file(os.path.normpath(record_path + uav + '_' + str(time.time()) + '.png'), png_image)

def airsim_getimages(client,  uav_id):
    image = client.simGetImage("0", airsim.ImageType.Scene,  vehicle_name=uav_id)
    return image

def dft_codebook(dim):
    seq = np.matrix(np.arange(dim))
    mat = seq.conj().T * seq
    w = np.exp(-1j * 2 * np.pi * mat / dim)
    return w

def get_ula_beamangles(wt, Nt, beam_index):
    # Nt = Number of antennas ; target = Target ID ; Plot = Plot radiantion pattern ; all_angles = return angle for all ID
    theta = np.linspace(-np.pi,np.pi,500) #Angular domain
    theta = theta[:, np.newaxis]
    Roffset = 0.008 # Offset to define the radiation peak
    arrayFactors = arrayFactorGivenAngleForULA(Nt,theta,angleWithArrayNormal=0)
    steeredArrayFactors = np.squeeze(np.matmul(arrayFactors, wt))

    radiantion = []
    maxR = np.amax(abs(steeredArrayFactors[:,beam_index]))
    indices = np.where((abs(steeredArrayFactors[:,beam_index])<maxR + Roffset) & (abs(steeredArrayFactors[:,beam_index])>maxR - Roffset))
    for indx in list(indices[0]):
        angles = np.rad2deg(theta[indx])
        radiantion.append(float(angles))

    #plt.figure()
    #plt.title('Beams\n')
    #plt.subplot(projection='polar') # Just work with Python3.6 or less (bizarre)
    #plt.polar(theta,abs(steeredArrayFactors[:,beam_index]))
    #plt.show()
    ula_angle = max(radiantion)

    return ula_angle

def linecount(eps):
    if len(eps)<2:
        all_eps = [int(eps[0])]
    else:
        all_eps = list(range(int(eps[0]), int(eps[1])+1))
    count = 0
    for ep in all_eps:
        episode_file = open(f"./episodes/ep{int(ep)}.csv", 'r') 
        for line in episode_file:
            line = line.split(',')
            if line[1] == 'uav1':
                count += 1
        episode_file.close()
    return count
