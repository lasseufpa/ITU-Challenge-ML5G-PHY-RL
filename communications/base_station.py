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

	def __init__(self, Elements = 64, frequency = 60e9,bandwidth = 100e6, name='', ep_lenght = 200, traffic_type = 'light', BS_type = 'ULA'):
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

	def packages(self, traffic, packet_size):
		""" 
		Alocate packages for each user in a time slot (10ms)
		"""
		np.random.poisson(lam=(1e7/packet_size))
		if traffic == 'light': # 1Gbps -> 1e7Gb per 10ms
			package_capacity = np.floor(np.random.poisson(lam=(1e7/packet_size)))
		elif traffic == 'dense': # 3Gpbs -> 3e7Gb per 10ms
			package_capacity = np.ceil(np.random.poisson(lam=(3e7/packet_size)))	
		else:
			raise TypeError("It's not a valid type of traffic")
		return package_capacity

		
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
		packets = self.packages(self._traffic_type, self.UEs[target].packet_size)
		reward = self.H_mag(target, action)
		self.Bit_rate(reward,440.35)
		self.UEs[target].step(packets, self.R)

		# Step for not target UE's 
		for i in range(len(self.UEs)):
			if i != target:
				d_packets = self.packages(self._traffic_type, self.UEs[i].packet_size)
				self.UEs[i].step(d_packets, 0)

		self._state += 1
		done = self._state >= self.ep_lenght
		feedback = self.UE_feedback(target) 
		feedback.append(float(self.R))# dropped packets, sent packets and bit rate
		state = np.concatenate((self.UEs[target].position, feedback), axis=None)
		return state, reward, feedback, done  

	def UE_feedback(self, target):
		"""
        Return the packets feedback from target UE
        """
		dropped = 0
		for i in range(len(self.UEs)):
			dropped += self.UEs[i].dropped_packets
			
		return [dropped, self.UEs[target].sent_packets]
		

	def clear(self):
		"""
        Clear base stations atributes
        """
		self._channel = None
		self._state = 0
		self.num_resets += 1
		return self._state