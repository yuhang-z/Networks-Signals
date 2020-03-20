import inspect
import cmath
import numpy as np
from math import log, ceil
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy import fftpack
from matplotlib.colors import LogNorm


def DFT_slow(x):
    """Compute the discrete Fourier Transform of the 1D array x"""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    n = np.arange(N)
    k = n.reshape((N, 1))
    M = np.exp(-2j * np.pi * k * n / N)
    return np.dot(M, x)
    # t = []
    # N = len(x)
    # for k in range(N):
    #     a = 0
    #     for n in range(N):
    #         a += x[n]*np.exp(-2j*np.pi*k*n*(1/N))
    #     t.append(a)
    # return np.asarray(t)


def IDFT_slow(x):
    """Compute the inverse discrete Fourier Transform of the 1D array x"""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    n = np.arange(N)
    k = n.reshape((N, 1))
    M = np.exp(2j * np.pi * k * n / N)
    return np.dot(M, x)
    # x = []
    # N = len(t)
    # for n in range(N):
    #     a = 0
    #     for k in range(N):
    #         a += t[k]*np.exp(2j*np.pi*k*n*(1/N))
    #     a /= N
    #     x.append(a)
    # return np.asarray(x)


def FFT(x):
    """A recursive implementation of the 1D Cooley-Tukey FFT"""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]

    if N % 2 > 0:
        raise ValueError("size of x must be a power of 2")
    elif N <= 32:  # this cutoff should be optimized
        return DFT_slow(x)
    else:
        X_even = FFT(x[::2])
        X_odd = FFT(x[1::2])
        factor = np.exp(-2j * np.pi * np.arange(N) / N)
        return np.concatenate([X_even + factor[:int(N / 2)] * X_odd,
                               X_even + factor[int(N / 2):] * X_odd])


def FFT_inverse(x):
    x = np.asarray(x, dtype=float)
    N = x.shape[0]

    if N % 2 > 0:
        raise ValueError("size of x must be a power of 2")
    elif N <= 32:  # this cutoff should be optimized
        return IDFT_slow(x)
    else:
        X_even = FFT_inverse(x[::2])
        X_odd = FFT_inverse(x[1::2])
        factor = np.exp(2j * np.pi * np.arange(N) / N)
        return np.concatenate([X_even + factor[:int(N / 2)] * X_odd,
                               X_even + factor[int(N / 2):] * X_odd])


def IDFT(x):
    return list(map(lambda a: a / len(x), IDFT_slow(x)))


def IFFT(x):
    return list(map(lambda a: a / len(x), FFT_inverse(x)))


def twoFFT(x):
    """ x is inported and modified as a 2-d array"""
    m, n = x.shape
    return np.array([ [ sum([ sum([ x[i,j]*np.exp(-1j*2*np.pi*(k_m*i/m + k_n*j/n)) for i in range(m) ]) for j in range(n) ]) for k_n in range(n) ] for k_m in range(m) ])
        


def twoIFFT(x):
    m, n = x.shape
    for k in range(m):
        for l in range(n):
            x[k,l] = sum([ sum([ x[i,j]*np.exp(j*2*np.pi*(k*i/m + l*j/n)) for i in range(m) ]) for j in range(n)])
    return x   


mode = 0
address = "moonlanding.png"

def plot_spectrum(im_fft):
    from matplotlib.colors import LogNorm
    # A logarithmic colormap
    plt.imshow(np.abs(im_fft), norm=LogNorm(vmin=5))
    plt.colorbar()

# mode manipulation
def modeOutput(mode, address):
    if(mode == 1):
        print("mode 1 is triggered")

        # img is a 2-d array 
        img_original = mpimg.imread(address)

        #img_FFT = twoFFT(img_original)
        img_FFT = fftpack.fft2(img_original)

        plt.figure("Mode_1")
        plt.subplot(211)
        plt.imshow(img_original)
        
        plt.subplot(212)
        plt.imshow(np.abs(img_FFT), norm=LogNorm(vmin=5))
        plt.show()

    if(mode == 2):
        print("mode 2 is triggered")
        keep_fraction = 0.09

        # Call ff a copy of the original transform. Numpy arrays have a copy
        # method for this purpose.
        img_original = mpimg.imread(address)

        im_fft2 = fftpack.fft2(img_original)


        # Set r and c to be the number of rows and columns of the array.
        r, c = im_fft2.shape

        # Set to zero all rows with indices between r*keep_fraction and
        # r*(1-keep_fraction):
        im_fft2[int(r*keep_fraction):int(r*(1-keep_fraction))] = 0.0

        # Similarly with the columns:
        im_fft2[:, int(c*keep_fraction):int(c*(1-keep_fraction))] = 0.0

        #plt.figure()
        img_new = fftpack.ifft2(im_fft2).real
        plt.figure("Mode_2")
        plt.subplot(211)
        plt.imshow(img_original)
        
        plt.subplot(212)
        plt.imshow(img_new)
        plt.show()

    if(mode == 3):
        T = 0.1
        c = F3 * (P3 >= T)
        fM = ifft2(c)*W*H
        plt.imshow(np.abs(fM));    






if __name__ == '__main__':
    # If there are more than two inputs, exit
    if len(sys.argv) > 3:
        print("Invalid inputs!\tpython fft.py [-m mode] [-i image]")
        exit(1)

    # Case 1: no input: default mode and address
    elif len(sys.argv) == 1:
        pass

    # Case 2: Two inputs: mode and address
    elif len(sys.argv) == 3:
        try:  # Is this a number?
            mode = int(sys.argv[1])
        except ValueError:
            print("Invalid mode input! Mode should be inputted 1, 2, 3, or 4!\tYour input: " + sys.argv[1])
            exit(1)
        else:  # Check if mode is in range of [1, 4]
            if not 1 <= mode <= 4:
                print("Invalid mode input! Mode should be inputted 1, 2, 3, or 4!\tYour input: " + sys.argv[1])
                exit(1)

        # Is this a valid address?
        if not os.path.isfile(sys.argv[2]):
            print("Invalid image input! Filename does not exist!\tYour input: " + sys.argv[2])
            exit(1)
        else:
            address = sys.argv[2]

        """ function call """
        modeOutput(mode, address)    

    # Case 3: One input: either mode or address
    else:
        try:  # Is this a number?
            mode = int(sys.argv[1])
        except ValueError:  # If not, is this a valid address?
            if not os.path.isfile(sys.argv[1]):
                print("Invalid image input! Filename does not exist!\tYour input: " + sys.argv[1])
                exit(1)
            else:
                address = sys.argv[1]
        else:
            # Check if mode is in range of [1, 4]
            if not 1 <= mode <= 4:
                print("Invalid mode input! Mode should be inputted 1, 2, 3, or 4!\tYour input: " + sys.argv[1])
                exit(1)

        x = np.random.random(1024)
        print(np.allclose(FFT(x), np.fft.fft(x)))
        print(np.allclose(IFFT(x), np.fft.ifft(x)))
