#Script context use	: This script is for CAVIAR purposes uses
#Author       		: Ailton Oliveira
#Email          	: ailton.pinto@itec.ufpa.br

import numpy as np
import matplotlib.pyplot as plt
from .caviar_channel import ULAchannel, UPAchannel, chosen_precoder, ULA_best_beam

class BaseStation():
	
	@staticmethod 
	def dft_codebook(dim):
		"""
        Codebook based in DFT
        """
		seq = np.matrix(np.arange(dim))
		mat = seq.conj().T * seq
		w = np.exp(-1j * 2 * np.pi * mat / dim)
		return w

	def __init__(self, Elements = 64, frequency = 60e9,bandwidth = 100e6, name='', ep_lenght = 200, traffic_type = 'light', BS_type = 'ULA', change_type=False):
		self._NTx = Elements # NUmber of MIMO elements in BS
		self.codebook_tx = self.dft_codebook(Elements)
		self.Channel = None # Channel matrix
		self.frequency = frequency # Carrier Frequency
		self._ID = name # BS name
		self._state = 0 # State 
		self.num_resets = 0 # Number of resets in simulation
		self.ep_lenght = ep_lenght # Episode duration
		self.se = 1 #Spectral Efficiency 
		self.bandwidth = bandwidth # Bandwidth
		self.UEs = [] # List with User equipaments objects
		self._type = BS_type 
		self._traffic_type = traffic_type
		self.R = 0
		self.change_type = change_type

	@property
	def ID(self):
		return self._ID

	@property
	def NTx(self):
		return self._NTx
	
	@property
	def user_list(self):
		return self.UEs

	def append(self, Ue_object):
		"""
        Create a list of UE objects associates to the BS
        """
		self.UEs.append(Ue_object)

	def Bit_rate(self, H, const):
		"""
		Calculate Bit_rate in the channel
        SINR = (Pt*|H²|)/(P_noise*σ²)
		const = Pt/((P_noise*σ²)) 
		SE = Log2(1+SINR) --> R = Bandwith * SE
		1 Gbps < R < 3 Gbps
        """
		SINR = const * (H**2)
		self.se = np.log2(1+SINR)
		self.R = float(self.bandwidth * self.se)

	def packages(self, traffic, packet_size, ue_type):
		""" 
		Alocate packages for each user in a time slot (10ms)
		"""
		if traffic == "light":  # 1Gbps -> 1e7Gb per 10ms
			total_throughput = 6e7
		elif traffic == "dense":  # 3Gpbs -> 3e7Gb per 10ms
			total_throughput = 12e7
		else:
			raise TypeError("It's not a valid type of traffic")

		if ue_type == "UAV":
			throughput = np.floor(
				np.random.poisson(lam=(0.5 * total_throughput) / packet_size)
			)
		elif ue_type == "CAR":
			throughput = np.floor(
				np.random.poisson(lam=(0.3 * total_throughput) / packet_size)
			)
		elif ue_type == "PED":
			throughput = np.floor(
				np.random.poisson(lam=(0.2 * total_throughput) / packet_size)
			)
		else:
			raise TypeError("Invalid UE type")

		return throughput
		
	def H_matrix(self, target):
		"""
        Update channel value based in actual UE position
        """
		position = self.UEs[target].position
		if self._type == 'ULA':
			self.Channel = ULAchannel(position,frequency=self.frequency, Nt = self.NTx)
		elif self._type == 'UPA':
			self.Channel = UPAchannel(position,frequency=self.frequency, Nt = self.NTx)
		else:
			raise TypeError("It's not a valid type of model")

	def H_mag(self, target, index):
		"""
        Magnitude of channel with the chosen precoder(beam index)
        """ 
		self.H_matrix(target)
		Ht = chosen_precoder(index,self.Channel,self.codebook_tx)
		#noise = np.random.normal(0, .1, Ht.shape)
		return np.squeeze(np.array(Ht))

	def best_beam(self):
		"""
        Best choose of beam (Brute force)
        """ 
		best_index = ULA_best_beam(self.Channel, self.codebook_tx)
		return best_index

	def step(self, target, action):
		"""
        Executes the BS channel processing integrate with UE packets processing.
        """
		packets = self.packages(self._traffic_type, self.UEs[target].packet_size, self.UEs[target].obj_type)
		channel_mag = self.H_mag(target, action)
		self.Bit_rate(channel_mag,440.35)
		self.UEs[target].step(packets, self.R)

		# Step for not target UE's 
		for i in range(len(self.UEs)):
			if i != target:
				d_packets = self.packages(self._traffic_type, self.UEs[i].packet_size, self.UEs[i].obj_type)
				self.UEs[i].step(d_packets, 0)

		self._state += 1
		if self.change_type:
			update_traffic = self._state % 1000
			if not update_traffic:
				if self._traffic_type == 'dense':
					self._traffic_type = 'light'
				else:
					self._traffic_type = 'dense'

		done = self._state >= self.ep_lenght
		feedback = self.UE_feedback(target)# dropped packets, sent packets and buffered packets 
		feedback.append(float(self.R))# dropped packets, sent packets, buffered packets and bitrate
		info = feedback[:]
		info.append(str(self.UEs[target]._ID))# dropped packets, sent packets, buffered packets, bitrate and ue_name
		info.append(packets)# dropped packets, sent packets, buffered packets, bitrate, ue_name and packets
		info.append(channel_mag)# dropped packets, sent packets, buffered packets, bitrate, ue_name, packets and channel_mag
		dropped_packets = info[0]
		sent_packets = info[1]
		buffered_packets = info[2]
		
		if buffered_packets > 0:
			reward = (sent_packets - 2*dropped_packets)/buffered_packets
		else:
			reward = 0

		state = np.concatenate((self.UEs[target]._position, feedback), axis=None)
		return state, reward, info, done 
	
	def best_beam_step(self, target):
		"""
        Executes the BS channel processing integrate with UE packets processing.
        """
		packets = self.packages(self._traffic_type, self.UEs[target].packet_size, self.UEs[target].obj_type)
		self.H_matrix(target)
		index = self.best_beam()
		reward = np.squeeze(np.array(chosen_precoder(index,self.Channel,self.codebook_tx)))
		self.Bit_rate(reward,440.35)
		self.UEs[target].step(packets, self.R)

		# Step for not target UE's 
		for i in range(len(self.UEs)):
			if i != target:
				d_packets = self.packages(self._traffic_type, self.UEs[i].packet_size, self.UEs[i].obj_type)
				self.UEs[i].step(d_packets, 0)

		self._state += 1
		if self.change_type:
			update_traffic = self._state % 1000
			if not update_traffic:
				if self._traffic_type == 'dense':
					self._traffic_type = 'light'
				else:
					self._traffic_type = 'dense'
				
		done = self._state >= self.ep_lenght
		feedback = self.UE_feedback(target)# dropped packets and sent packets 
		feedback.append(float(self.R))# dropped packets, sent packets and bitrate
		info = feedback[:]
		info.append(str(self.UEs[target]._ID))# dropped packets, sent packets, bitrate and ue_name
		info.append(index)
		info.append(packets)
		state = np.concatenate((self.UEs[target]._position, feedback), axis=None)
		return state, reward, info, done  

	def UE_feedback(self, target):
		"""
        Return the packets feedback from target UE
        """
		dropped = 0
		for i in range(len(self.UEs)):
			dropped += self.UEs[i].dropped_packets
			
		return [dropped, self.UEs[target].sent_packets, np.sum(self.UEs[target].buffer)]
		

	def clear(self):
		"""
        Clear base stations atributes
        """
		self._channel = None
		self._state = 0
		self.num_resets += 1
		return self._state