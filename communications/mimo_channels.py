import os
import datetime
import numpy as np

def calc_omega(elevationAngles, azimuthAngles, normalizedAntDistance = 0.5):
    sinElevations = np.sin(elevationAngles)
    omegax = 2 * np.pi * normalizedAntDistance * sinElevations * np.cos(azimuthAngles)
    omegay = 2 * np.pi * normalizedAntDistance * sinElevations * np.sin(azimuthAngles)
    return np.matrix((omegax, omegay))

def getNarrowBandUPAMIMOChannel(departureElevation,departureAzimuth,arrivalElevation,arrivalAzimuth, p_gainsdB,
                                number_Tx_antennasX, number_Tx_antennasY, number_Rx_antennasX,
                                number_Rx_antennasY, pathPhases = None, normalizedAntDistance=0.5):
    """Uses UPAs at both TX and RX.
    Will assume that all 4 normalized distances (Tx and Rx, x and y) are the same.
    """
    number_Tx_antennas = number_Tx_antennasX * number_Tx_antennasY
    number_Rx_antennas = number_Rx_antennasX * number_Rx_antennasY
    departureElevation = np.deg2rad(departureElevation)
    departureAzimuth = np.deg2rad(departureAzimuth)
    arrivalElevation = np.deg2rad(arrivalElevation)
    arrivalAzimuth = np.deg2rad(arrivalAzimuth)

    numRays = np.shape(departureElevation)[0]
    #number_Rx_antennas is the total number of antenna elements of the array, idem Tx
    H = np.matrix(np.zeros((number_Rx_antennas, number_Tx_antennas)))

    path_gain = np.power(10, p_gainsdB / 10)

    #generate uniformly distributed random phase in radians
    if pathPhases is None:
        pathPhases = 2*np.pi * np.random.rand(len(path_gain))
    else:
        #convert from degrees to radians the phase obtained with simulator (InSite)
        pathPhases = np.deg2rad(pathPhases)

    #include phase information, converting gains in complex-values
    path_complexGains = path_gain * np.exp(1j * pathPhases)

    # recall that in the narrowband case, the time-domain H is the same as the
    # frequency-domain H
    # Each vector below has the x and y values for each ray. Example 2 x 25 dimension
    departure_omega = calc_omega(departureElevation, departureAzimuth, normalizedAntDistance)
    arrival_omega = calc_omega(arrivalElevation, arrivalAzimuth, normalizedAntDistance)

    rangeTx_x = np.arange(number_Tx_antennasX)
    rangeTx_y = np.arange(number_Tx_antennasY)
    rangeRx_x = np.arange(number_Rx_antennasX)
    rangeRx_y = np.arange(number_Rx_antennasY)
    for ray_i in range(numRays):
        #departure
        vecx = np.exp(1j * departure_omega[0,ray_i] * rangeTx_x)
        vecy = np.exp(1j * departure_omega[1,ray_i] * rangeTx_y)
        departure_vec = np.matrix(np.kron(vecy, vecx))
        #arrival
        vecx = np.exp(1j * arrival_omega[0,ray_i] * rangeRx_x)
        vecy = np.exp(1j * arrival_omega[1,ray_i] * rangeRx_y)
        arrival_vec = np.matrix(np.kron(vecy, vecx))

        H = H + path_complexGains[ray_i] * arrival_vec.conj().T * departure_vec
    return H


def getNarrowBandULAMIMOChannel(azimuths_tx, azimuths_rx, p_gainsdB, number_Tx_antennas, number_Rx_antennas,
                                normalizedAntDistance=0.5, angleWithArrayNormal=0, pathPhases=None):
    """This .m file uses ULAs at both TX and RX.

    - assumes one beam per antenna element

    the first column will be the elevation angle, and the second column is the azimuth angle correspondingly.
    p_gain will be a matrix size of (L, 1)
    departure angle/arrival angle will be a matrix as size of (L, 2), where L is the number of paths

    t1 will be a matrix of size (nt, nr), each
    element of index (i,j) will be the received
    power with the i-th precoder and the j-th
    combiner in the departing and arrival codebooks
    respectively

    :param departure_angles: ((elevation angle, azimuth angle),) (L, 2) where L is the number of paths
    :param arrival_angles: ((elevation angle, azimuth angle),) (L, 2) where L is the number of paths
    :param p_gaindB: path gain (L, 1) in dB where L is the number of paths
    :param number_Rx_antennas, number_Tx_antennas: number of antennas at Rx and Tx, respectively
    :param pathPhases: in degrees, same dimension as p_gaindB
    :return:
    """
    azimuths_tx = np.deg2rad(azimuths_tx)
    azimuths_rx = np.deg2rad(azimuths_rx)
    # nt = number_Rx_antennas * number_Tx_antennas #np.power(antenna_number, 2)
    m = np.shape(azimuths_tx)[0]  # number of rays
    H = np.matrix(np.zeros((number_Rx_antennas, number_Tx_antennas)))

    gain_dB = p_gainsdB
    path_gain = np.power(10, gain_dB / 10)
    path_gain = np.sqrt(path_gain)

    #generate uniformly distributed random phase in radians
    if pathPhases is None:
        pathPhases = 2*np.pi * np.random.rand(len(path_gain))
    else:
        #convert from degrees to radians
        pathPhases = np.deg2rad(pathPhases)

    #include phase information, converting gains in complex-values
    path_complexGains = path_gain * np.exp(-1j * pathPhases)

    # recall that in the narrowband case, the time-domain H is the same as the
    # frequency-domain H
    for i in range(m):
        # at and ar are row vectors (using Python's matrix)
        at = np.matrix(arrayFactorGivenAngleForULA(number_Tx_antennas, azimuths_tx[i], normalizedAntDistance,
                                                   angleWithArrayNormal))
        ar = np.matrix(arrayFactorGivenAngleForULA(number_Rx_antennas, azimuths_rx[i], normalizedAntDistance,
                                                   angleWithArrayNormal))
        H = H + path_complexGains[i] * ar.conj().T * at  # outer product of ar Hermitian and at
    #factor = (np.linalg.norm(path_complexGains) / np.sum(path_complexGains)) * np.sqrt(
    #    number_Rx_antennas * number_Tx_antennas)  # scale channel matrix
    #H *= factor  # normalize for compatibility with Anum's Matlab code

    return H

def arrayFactorGivenAngleForULA(numAntennaElements, theta, normalizedAntDistance=0.5, angleWithArrayNormal=0):
    '''
    Calculate array factor for ULA for angle theta. If angleWithArrayNormal=0
    (default),the angle is between the input signal and the array axis. In
    this case when theta=0, the signal direction is parallel to the array
    axis and there is no energy. The maximum values are for directions 90
        and -90 degrees, which are orthogonal with array axis.
    If angleWithArrayNormal=1, angle is with the array normal, which uses
    sine instead of cosine. In this case, the maxima are for
        thetas = 0 and 180 degrees.
    References:
    http://www.waves.utoronto.ca/prof/svhum/ece422/notes/15-arrays2.pdf
    Book by Balanis, book by Tse.
    '''
    indices = np.arange(numAntennaElements)
    if (angleWithArrayNormal == 1):
        arrayFactor = np.exp(1j * 2 * np.pi * normalizedAntDistance * indices * np.sin(theta))
    else:  # default
        arrayFactor = np.exp(1j * 2 * np.pi * normalizedAntDistance * indices * np.cos(theta))
    arrayFactor = arrayFactor / np.sqrt(numAntennaElements)
    return arrayFactor  # normalize to have unitary norm

def arrayPatternUPA(numAntennasX, numAntennasY, azimuths, elevations, wx, wy, normalizedDistX=0.5, normalizedDistY =0.5):
    #function upaArrayFactor = arrayPatternUPA(numAntennasX, numAntennasY, ...
    #    azimuths, elevations, normalizedDistX, normalizedDistY, wx, wy)
    #Adapted from Eqs. (6.7) and (6.85) of Balanis' book. It is more general
    #than Eqs. (6.7) and (6.85) in the sense
    #that supports arbitrary precoding vectors wx and wy, while (6.85) assumes
    #linear phase beta.
    phi=azimuths
    theta=elevations
    #Angle Psi but without incorporating the pointing angle beta in (6.85)
    psiAngleX=2*np.pi*normalizedDistX*np.sin(theta)*np.cos(phi)
    #consider below the case of n=0: all angles x are zero and e^jx = 1
    arrayFactorsX = np.zeros((psiAngleX.shape))#np.zeros(size(psiAngleX))
    #complete the summation with other parcels:
    for n in range(0, numAntennasX):#n=1:numAntennasX
        #arrayFactorsX = arrayFactorsX + exp(1j*((n-1)*psiAngleX + wx(n)));
        arrayFactorsX = arrayFactorsX + np.exp(1j*((n-1)*psiAngleX))*wx[n]
        
    #Angle Psi but without incorporating the pointing angle beta in (6.85)
    psiAngleY=2*np.pi*normalizedDistY*np.sin(theta)*np.sin(phi)
    #consider below the case of n=0: all angles x are zero and e^jx = 1
    arrayFactorsY = np.zeros((psiAngleY.shape))#np.zeros(size(psiAngleY))
    #complete the summation with other parcels:
    for n in range(0, numAntennasY):#n=1:numAntennasY
        #arrayFactorsY = arrayFactorsY + exp(1j*((n-1)*psiAngleY + wy(n)));
        arrayFactorsY = arrayFactorsY + np.exp(1j*((n-1)*psiAngleY))*wy[n]

    upaArrayFactor = np.multiply(arrayFactorsX, arrayFactorsY)
    #normalize
    upaArrayFactor = upaArrayFactor / np.sqrt(numAntennasX*numAntennasY)
    return upaArrayFactor

def getCodebookOperatedChannel(H, Wt, Wr):
    if Wr is None: #only 1 antenna at Rx, and Wr was passed as None
        return H * Wt
    if Wt is None: #only 1 antenna at Tx
        return Wr.conj().T * H
    return Wr.conj().T * H * Wt # return equivalent channel after precoding and combining
