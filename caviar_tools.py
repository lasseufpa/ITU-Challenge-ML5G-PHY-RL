'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Takashi, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git


Auxiliary methods for CAVIAR simulations
V1.0
'''

import caviar_config
import airsim
import csv
import time
import os
import numpy as np

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

def all_info_csv(user_id,episode):
    with open('./episodes/ep{}.csv'.format(episode)) as cs:
        episode_data = csv.DictReader(cs)
        loop = -1
        for row in episode_data:
            if row['obj'] == user_id:
                loop += 1
                values = row.values()
                array = np.asarray(list(values)) #convert to float
                if loop == 0:
                    info = array            
                    continue     
                info = np.vstack((info, array))
    return info


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

def unreal_getpose(client, obj_id):
    coordinates =  client.simGetObjectPose(obj_id).position.to_numpy_array()
    return coordinates

def unreal_getorientation(client, obj_id):
    orientation =  client.simGetObjectPose(obj_id).orientation.to_numpy_array()
    return orientation

def airsim_save_images(client, record_path = './'):
    for uav in caviar_config.drone_ids:
        png_image = client.simGetImage("0", airsim.ImageType.Scene,  vehicle_name=uav)
        airsim.write_file(os.path.normpath(record_path + uav + '_' + str(time.time()) + '.png'), png_image)

'''
Get the episodes csv's and return a list of dataframes
in which each element corresponds to the information 
of an episode.

:param eps: (array of integers) defines the episodes 
                                   to get info from.

Example: To get episodes 0, 10 and 20, then: 
eps = [0, 10, 20]
'''
'''
def read_episode_csv(eps):
    episodes=[]
    for ep in eps:
        episodes.append(pd.read_csv('./episodes/ep'+
        str(ep)+'.csv', sep=',', header = None))
    return episodes

'''
'''
Get the user position from the episode file(s).

:param eps: (array of integers) defines the episodes 
                                   to get info from.

Example: To get episodes 0, 10 and 20, then: 
eps = [0, 10, 20]

:param ue_name: (str) name of the UE to get info from.
'''
'''
def get_pos_from_csv(eps, ue_name, get_all_info):
    if get_all_info:
        ue_x = np.array([])
        ue_y = np.array([])
        ue_z = np.array([])
        ue_orien_w = np.array([])
        ue_orien_x = np.array([])
        ue_orien_y = np.array([])
        ue_orien_z = np.array([])
        ue_linear_acc_x = np.array([])
        ue_linear_acc_y = np.array([])
        ue_linear_acc_z = np.array([])
        ue_linear_vel_x = np.array([])
        ue_linear_vel_y = np.array([])
        ue_linear_vel_z = np.array([])
        ue_angular_acc_x = np.array([])
        ue_angular_acc_y = np.array([])
        ue_angular_acc_z = np.array([])
        ue_angular_vel_x = np.array([])
        ue_angular_vel_y = np.array([])
        ue_angular_vel_z = np.array([])
        episode = read_episode_csv(eps=eps)
        for ep in episode:
            ue_df = ep.loc[ep[1] == ue_name]
            ue_x = np.concatenate((ue_x, ue_df.iloc[:,2].values), axis=None).astype(float)
            ue_y = np.concatenate((ue_y, ue_df.iloc[:,3].values), axis=None).astype(float)
            ue_z = np.concatenate((ue_z, ue_df.iloc[:,4].values), axis=None).astype(float)
            ue_orien_w = np.concatenate((ue_orien_w, ue_df.iloc[:,5].values), axis=None).astype(float)
            ue_orien_x = np.concatenate((ue_orien_x, ue_df.iloc[:,6].values), axis=None).astype(float)
            ue_orien_y = np.concatenate((ue_orien_y, ue_df.iloc[:,7].values), axis=None).astype(float)
            ue_orien_z = np.concatenate((ue_orien_z, ue_df.iloc[:,8].values), axis=None).astype(float)
            ue_linear_acc_x = np.concatenate((ue_linear_acc_x, ue_df.iloc[:,9].values), axis=None).astype(float)
            ue_linear_acc_y = np.concatenate((ue_linear_acc_y, ue_df.iloc[:,10].values), axis=None).astype(float)
            ue_linear_acc_z = np.concatenate((ue_linear_acc_z, ue_df.iloc[:,11].values), axis=None).astype(float)
            ue_linear_vel_x = np.concatenate((ue_linear_vel_x, ue_df.iloc[:,12].values), axis=None).astype(float)
            ue_linear_vel_y = np.concatenate((ue_linear_vel_y, ue_df.iloc[:,13].values), axis=None).astype(float)
            ue_linear_vel_z = np.concatenate((ue_linear_vel_z, ue_df.iloc[:,14].values), axis=None).astype(float)
            ue_angular_acc_x = np.concatenate((ue_angular_acc_x, ue_df.iloc[:,15].values), axis=None).astype(float)
            ue_angular_acc_y = np.concatenate((ue_angular_acc_y, ue_df.iloc[:,16].values), axis=None).astype(float)
            ue_angular_acc_z = np.concatenate((ue_angular_acc_z, ue_df.iloc[:,17].values), axis=None).astype(float)
            ue_angular_vel_x = np.concatenate((ue_angular_vel_x, ue_df.iloc[:,18].values), axis=None).astype(float)
            ue_angular_vel_y = np.concatenate((ue_angular_vel_y, ue_df.iloc[:,19].values), axis=None).astype(float)
            ue_angular_vel_z = np.concatenate((ue_angular_vel_z, ue_df.iloc[:,20].values), axis=None).astype(float)
        info = [ue_x, ue_y, ue_z, ue_orien_w, ue_orien_x,
                ue_orien_y, ue_orien_z, ue_linear_acc_x, ue_linear_acc_y,
                ue_linear_acc_z, ue_linear_vel_x, ue_linear_vel_y, ue_linear_vel_z,
                ue_angular_acc_x, ue_angular_acc_y, ue_angular_acc_z, ue_angular_vel_x,
                ue_angular_vel_y, ue_angular_vel_z]
    else:
        ue_x = np.array([])
        ue_y = np.array([])
        ue_z = np.array([])
        episode = read_episode_csv(eps=eps)
        for ep in episode:
            ue_df = ep.loc[ep[1] == ue_name]
            ue_x = np.concatenate((ue_x, ue_df.iloc[:,2].values), axis=None).astype(float)
            ue_y = np.concatenate((ue_y, ue_df.iloc[:,3].values), axis=None).astype(float)
            ue_z = np.concatenate((ue_z, ue_df.iloc[:,4].values), axis=None).astype(float)
            
        info = [ue_x, ue_y, ue_z]
    return info
    '''