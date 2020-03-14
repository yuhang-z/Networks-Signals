import inspect

import numpy as np
import sys
import os


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


mode = 1
address = "moonlanding.png"

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
