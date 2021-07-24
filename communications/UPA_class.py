import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class UPA:
    def __init__(self, N_elements_x, N_elements_y, phi = np.linspace(0,2*np.pi,200), theta = np.linspace(0,np.pi,200), normDistanceX = 0.5, normDistanceY = 0.5, pointAz = 0, pointEl = 0, N = 200):
        self.phi = phi # Angular domain
        self.theta = theta # Angular domain
        self.Nax = N_elements_x  # Number of antenna elements in X axis
        self.Nay = N_elements_y # Number of antenna elements in Y axis
        self.normDistanceX = normDistanceX # Normalized distance between the elements in X axis
        self.normDistanceY = normDistanceY # Normalized distance between the elements in Y axis
        self.pointAz = pointAz # Pointing Angle
        self.pointEl = pointEl # Pointing Angle
        self.N = N  # Angle grid resolution

    def get_angles(self):
        return self.phi, self.theta

    def pointingPatternUPA(self):
        self.phi = np.linspace(0,2*np.pi,self.N) #angles
        self.theta = np.linspace(0,np.pi,self.N) #angles

        self.betax = -2*np.pi*self.normDistanceX*np.sin(self.pointEl)*np.cos(self.pointAz)
        self.betay= -2*np.pi*self.normDistanceY*np.sin(self.pointEl)*np.sin(self.pointAz)

        #linear phase
        self.wx = np.exp(1j*np.arange(0, self.Nax)*self.betax)
        self.wy = np.exp(1j*np.arange(0, self.Nay)*self.betay)

        self.THETAele, self.PHIazi = np.meshgrid(self.theta,self.phi)

        self.upaArrayFactor = self.arrayPatternUPA(self.wx, self.wy)
        return self.upaArrayFactor, self.THETAele, self.PHIazi

    def arrayPatternUPA(self, wx, wy):
        '''
        function upaArrayFactor = arrayPatternUPA(numAntennasX, numAntennasY, ...
            azimuths, elevations, normalizedDistX, normalizedDistY, wx, wy)
        Adapted from Eqs. (6.7) and (6.85) of Balanis' book. It is more general
        than Eqs. (6.7) and (6.85) in the sense
        that supports arbitrary precoding vectors wx and wy, while (6.85) assumes
        linear phase beta.'''
        self.THETAele, self.PHIazi = np.meshgrid(self.theta,self.phi)
        #Angle Psi but without incorporating the pointing angle beta in (6.85)
        self.psiAngleX=2*np.pi*self.normDistanceX*np.sin(self.THETAele)*np.cos(self.PHIazi)
        #consider below the case of n=0: all angles x are zero and e^jx = 1
        self.arrayFactorsX = np.zeros((self.psiAngleX.shape))#np.zeros(size(psiAngleX))
        #complete the summation with other parcels:
        for n in range(0, self.Nax):
            self.arrayFactorsX = self.arrayFactorsX + np.exp(1j*((n)*self.psiAngleX))*wx[n]
        #Angle Psi but without incorporating the pointing angle beta in (6.85)
        self.psiAngleY=2*np.pi*self.normDistanceY*np.sin(self.THETAele)*np.sin(self.PHIazi)
        #consider below the case of n=0: all angles x are zero and e^jx = 1
        self.arrayFactorsY = np.zeros((self.psiAngleY.shape))#np.zeros(size(psiAngleY))
        #complete the summation with other parcels:
        for n in range(0, self.Nay):
            self.arrayFactorsY = self.arrayFactorsY + np.exp(1j*((n)*self.psiAngleY))*wy[n]

        self.upaArrayFactor = self.arrayFactorsX * self.arrayFactorsY
        #normalize
        self.upaArrayFactor = self.upaArrayFactor / np.sqrt(self.Nax*self.Nay)
        return self.upaArrayFactor
    
    def ak_fftmtx(self, N, option=1):
        '''
        function [Ah, A] = ak_fftmtx(N, option)
        FFT direct Ah and inverse A matrices with 3 options for
        the normalization factors:
        1 (default) ->orthonormal matrices
        2->conventional discrete-time (DT) Fourier series
        3->used in Matlab/Octave, corresponds to samples of DTFT
        Example that gives the same result as Matlab/Octave:
        Ah=ak_fftmtx(4,3); x=[1:4]'; Ah*x, fft(x)'''
        W = np.exp(-1j*2*np.pi/N) #twiddle factor W_N
        Ah=np.zeros((N,N), dtype=complex) #pre-allocate space
        for n in range(0, N):#n=0:N-1 #create the matrix with twiddle factors
            for k in range(0, N):#k=0:N-1
                Ah[k,n] = W ** (n*k)
        #choose among three different normalizations
        if option == 1: #orthonormal (also called unitary)
            Ah = Ah/np.sqrt(N)
            A = np.conj(Ah)
        elif option == 2: #read X(k) in Volts in case x(n) is in Volts
            A = np.conj(Ah)
            Ah = Ah/N
        elif option == 3: #as in Matlab/Octave: Ah = Ah;
            A = np.conj(Ah)/N
        else:
            print(['Invalid option value: ', str(option)])
        return Ah, A

    def spherical_plot(self, upaArrayFactor):
        fig = plt.figure()
        ax = Axes3D(fig)

        # spherical to rectangular conversion
        x = np.absolute(upaArrayFactor)*np.sin(self.THETAele)*np.cos(self.PHIazi)
        y = np.absolute(upaArrayFactor)*np.sin(self.THETAele)*np.sin(self.PHIazi)
        z = np.absolute(upaArrayFactor)*np.cos(self.THETAele)

        disc = z.shape[0]

        # plot
        surf = ax.plot_surface(x, y, z, linewidth=0, antialiased=False)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()

    def dftweights(self):
        self.dftMatrixX, *_ = self.ak_fftmtx(self.Nax,3)
        self.dftMatrixY, *_ = self.ak_fftmtx(self.Nay,3) 
        return self.dftMatrixX, self.dftMatrixY

    def ArrayFactorUPA(self):
        dftMatrixX, dftMatrixY = self.dftweights()
        
        self.ArrayFactorupa = np.zeros((self.Nax, self.Nay, self.N, self.N), dtype=complex)
        for i in range(0, self.Nax):
            wx = dftMatrixX[:,i]
            for j in range(0, self.Nay):
                wy = dftMatrixY[:,j]
                upaArrayFactor = self.arrayPatternUPA(wx, wy)
                self.ArrayFactorupa[i,j,:,:] = upaArrayFactor

        self.ArrayFactorupa = self.ArrayFactorupa.reshape((self.Nax * self.Nay,self.N,self.N))
        #self.spherical_plot(self.ArrayFactorupa[indX,:,:])
        return self.ArrayFactorupa
'''
Nax=4 # Number of Tx antennas in x axis
Nay=4 # Number of Tx antennas in y axis

print('Test DFT Coodebook')
## test with DFT vectors                     
test2 = UPA(Nax, Nay)
test2.ArrayFactorUPA()'''