import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
from matplotlib.colors import LogNorm


def DFT_slow(inputArray):
    N = inputArray.size
    V = np.array([[np.exp(-2j * np.pi * v * y / N) for v in range(N)] for y in range(N)])
    return inputArray.dot(V)


def IDFT_slow(inputArray):
    N = inputArray.size
    V = np.array([[np.exp(2j * np.pi * v * y / N) for v in range(N)] for y in range(N)])
    return inputArray.dot(V)


def FFT(inputArray):
    inputArray = np.asarray(inputArray, dtype=float)
    N = inputArray.shape[0]

    if N % 2 > 0:
        raise ValueError("size of x must be a power of 2")
    elif N <= 32:  # this cutoff should be optimized
        return DFT_slow(inputArray)
    else:
        X_even = FFT(inputArray[::2])
        X_odd = FFT(inputArray[1::2])
        factor = np.exp(-2j * np.pi * np.arange(N) / N)
        return np.concatenate([X_even + factor[:int(N / 2)] * X_odd, X_even + factor[int(N / 2):] * X_odd])


def FFT_inverse(inputArray):
    inputArray = np.asarray(inputArray, dtype=complex)
    N = inputArray.shape[0]

    if N % 2 > 0:
        raise ValueError("size of x must be a power of 2")
    elif N <= 32:  # this cutoff should be optimized
        return IDFT_slow(inputArray)
    else:
        X_even = FFT_inverse(inputArray[::2])
        X_odd = FFT_inverse(inputArray[1::2])
        factor = np.exp(2j * np.pi * np.arange(N) / N)
        return np.concatenate([X_even + factor[:int(N / 2)] * X_odd, X_even + factor[int(N / 2):] * X_odd])


def FFT_2D(input2DArray):
    N = input2DArray.shape[1]
    if N % 2 > 0:
        raise ValueError("size of x must be a power of 2")
    elif N <= 32:  # this cutoff should be optimized
        return np.array([DFT_slow(input2DArray[i, :]) for i in range(input2DArray.shape[0])])
    else:
        X_even = FFT_2D(input2DArray[:, ::2])
        X_odd = FFT_2D(input2DArray[:, 1::2])
        factor = np.array([np.exp(-2j * np.pi * np.arange(N) / N) for i in range(input2DArray.shape[0])])
        return np.hstack([X_even + np.multiply(factor[:, :int(N / 2)], X_odd),
                          X_even + np.multiply(factor[:, int(N / 2):], X_odd)])


def IFFT_2D(input2DArray):
    N = input2DArray.shape[1]
    if N % 2 > 0:
        raise ValueError("size of x must be a power of 2")
    elif N <= 32:  # this cutoff should be optimized
        return np.array([IDFT_slow(input2DArray[i, :]) for i in range(input2DArray.shape[0])])
    else:
        X_even = IFFT_2D(input2DArray[:, ::2])
        X_odd = IFFT_2D(input2DArray[:, 1::2])
        factor = np.array([np.exp(2j * np.pi * np.arange(N) / N) for i in range(input2DArray.shape[0])])
        return np.hstack([X_even + np.multiply(factor[:, :int(N / 2)], X_odd),
                          X_even + np.multiply(factor[:, int(N / 2):], X_odd)])


def IDFT(inputArray):
    return list(map(lambda a: a / len(inputArray), IDFT_slow(inputArray)))


def IFFT(inputArray):
    return list(map(lambda a: a / len(inputArray), FFT_inverse(inputArray)))


def twoD_FFT(input2DArray):
    input2DArray = np.asarray(input2DArray, dtype=float)
    return FFT_2D(FFT_2D(input2DArray).T).T


def twoD_IFFT(input2DArray):
    input2DArray = np.asarray(input2DArray, dtype=complex)
    return np.array(
        list(map(lambda a: a / (len(input2DArray) * len(input2DArray[0])), IFFT_2D(IFFT_2D(input2DArray).T).T)))


def next_power_of_2(x):
    return 1 if x == 0 else 2 ** (x - 1).bit_length()


# mode manipulation
def modeOutput(mode, address):
    # img is a 2-d array
    img_original = cv2.imread(address, cv2.IMREAD_UNCHANGED)
    # img_original = mpimg.imread(address)
    vertical = img_original.shape[0]
    horizontal = img_original.shape[1]
    changed_vertical = next_power_of_2(vertical)
    changed_horizontal = next_power_of_2(horizontal)

    dsize = (changed_horizontal, changed_vertical)
    img_original = cv2.resize(img_original, dsize, interpolation=cv2.INTER_AREA)

    if mode == 1:
        print("mode 1 is triggered")

        # my function
        # img_FFT = twoD_FFT(img_original)

        # built-in function
        img_FFT = np.fft.fft2(img_original)

        plt.figure("Mode_1")
        plt.subplot(211)
        plt.imshow(img_original)

        plt.subplot(212)
        plt.imshow(np.abs(img_FFT), norm=LogNorm(vmin=5))
        plt.show()

    if mode == 2:
        print("mode 2 is triggered")
        keep_fraction = 0.09

        # Call ff a copy of the original transform. Numpy arrays have a copy
        # method for this purpose.

        # my function
        im_fft2 = twoD_FFT(img_original)

        # built-in function
        #im_fft2 = np.fft.fft2(img_original)

        r, c = im_fft2.shape
        im_fft2[int(r*keep_fraction):int(r*(1-keep_fraction))] = 0.0
        im_fft2[:, int(c*keep_fraction):int(c*(1-keep_fraction))] = 0.0

        #img_new = np.fft.ifft2(im_fft2).real
        img_new = twoD_IFFT(im_fft2).real

        plt.figure("Mode_2")
        plt.subplot(211)
        plt.imshow(img_original)

        plt.subplot(212)
        plt.imshow(img_new)
        plt.show()

    # if (mode == 3):
    # T = 0.1
    # c = F3 * (P3 >= T)
    # fM = ifft2(c) * W * H
    # plt.imshow(np.abs(fM));


if __name__ == '__main__':
    mode = 1
    address = "moonlanding.png"

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

    modeOutput(mode, address)
