#Script context use	: This script is for CAVIAR purposes uses
#Author       		: Ailton Oliveira
#Email          	: ailton.pinto@itec.ufpa.br

import numpy as np
from .buffer import Buffer
import caviar_tools


class UE(Buffer):
	
    def __init__(self, name='', buffer_size = 1e9, buffer_max_lat = 10, packet_size = 8188*8, obj_type = '', total_number_rbs = 17, episode = 0, use_airsim = False):
        Buffer.__init__(self, buffer_size, buffer_max_lat) 
        self._ID = name # Object ID
        self._state = 0 
        self._csv_positions=[]
        self._position = []  # Position [X,Y,Z]
        self.obj_type = obj_type # UAV or Unreal_object
        self.use_airsim = use_airsim
        if self.use_airsim:
            self.client = caviar_tools.airsim_connect() # Start Airsim
        else:
            self.client = None # None if will note use Airsim
            self.all_position = caviar_tools.positions_csv(name, episode)
            self.obj_type = 'CSV'
        #self._all_info = caviar_tools.all_info_csv(name, episode)
        #self.buffer_size = buffer_size
        self.packet_size = packet_size # size of sent/arrived packets
        self.total_number_rbs=total_number_rbs # resource blocks
    
    @property
    def ID(self):
        return self._ID
    
    '''
    @property
    def info(self):
        return self._all_info
    '''

    def get_pkt_throughput( self, RMbps):
        """
        Calculate the throughput available to be sent by the UE given the number
        of RBs allocated, bandwidth and the spectral efficiency. It is not the
        real throughput since the UE may have less packets in the buffer than
        the number of packets available to send.
        """
        pkt_throughput = np.floor((RMbps)/self.packet_size)
        return pkt_throughput

    @property
    def position(self):
        """
        Check if is a airsim UAV or other Unreal object(Car or pedestrians)
        and return a list as [x,y,z] -> [N,E,D] (Airsim domain)
        Important: -D is Up and +D is down
        """ 
        # TO-DO - Read CSV position dataset
        if self.obj_type == 'UAV':
            self._position = caviar_tools.airsim_getpose(self.client, self._ID)
        elif self.obj_type == 'PED' or self.obj_type == 'CAR' : 
            self._position = caviar_tools.unreal_getpose(self.client, self._ID)
        elif self.obj_type == 'CSV':
            tmp_list = next(self.all_position).split(',')
            self._position = [float(p) for p in tmp_list]
        elif self.obj_type == 'automated_test':
            self._position = [np.random.randint(10,50), np.random.randint(10,50), np.random.randint(-1,2)]
        else:
            raise TypeError("It's not a valid type of object")
        return self._position

    def client_reset(self):
        """
        Reset Airism client
        """
        caviar_tools.airsim_reset(self.client)
        self._state = 0

    def step(self,packets, R):
        """
        Executes the UE packets processing. Adding the received packets to the
        buffer and sending them in according to the throughput available and
        buffer.
        """
        pkt_throughput = self.get_pkt_throughput(R)
        Buffer.receive_packets(self, packets)
        Buffer.send_packets(self, pkt_throughput)
        self._state += 1
        return self.dropped_packets, self.sent_packets
	