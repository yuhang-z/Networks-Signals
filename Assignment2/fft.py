import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import time
import statistics
import matplotlib.image as mpimg
import cv2
from matplotlib.colors import LogNorm
import scipy.sparse
from tempfile import TemporaryFile
from numpy import savez_compressed


def DFT_slow(inputArray):
    N = inputArray.size
    V = np.array([[np.exp(-2j * np.pi * v * y / N) for v in range(N)] for y in range(N)])
    return inputArray.dot(V)


def IDFT_slow(inputArray):
    N = inputArray.size
    V = np.array([[np.exp(2j * np.pi * v * y / N) for v in range(N)] for y in range(N)])
    return inputArray.dot(V)


def IDFT(inputArray):
    return list(map(lambda a: a / len(inputArray), IDFT_slow(inputArray)))


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


def IFFT(inputArray):
    return list(map(lambda a: a / len(inputArray), FFT_inverse(inputArray)))


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


def twoD_FFT(input2DArray):
    input2DArray = np.asarray(input2DArray, dtype=float)
    return FFT_2D(FFT_2D(input2DArray).T).T


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


def twoD_IFFT(input2DArray):
    input2DArray = np.asarray(input2DArray, dtype=complex)
    return np.array(
        list(map(lambda a: a / (len(input2DArray) * len(input2DArray[0])), IFFT_2D(IFFT_2D(input2DArray).T).T)))


def DFT_2D(input2DArray):
    return np.array([DFT_slow(input2DArray[i, :]) for i in range(input2DArray.shape[0])])


def twoD_DFT(input2DArray):
    input2DArray = np.asarray(input2DArray, dtype=float)
    return DFT_2D(DFT_2D(input2DArray).T).T


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
        img_FFT = twoD_FFT(img_original)

        # built-in function
        # img_FFT = np.fft.fft2(img_original)

        plt.figure("Mode_1")
        plt.subplot(121)
        plt.imshow(img_original)

        plt.subplot(122)
        plt.imshow(np.abs(img_FFT), norm=LogNorm(vmin=5))
        plt.show()

    if mode == 2:
        print("mode 2 is triggered")
        keep_fraction = 0.15

        # Call ff a copy of the original transform. Numpy arrays have a copy
        # method for this purpose.

        # my function
        im_fft2 = twoD_FFT(img_original)

        # built-in function
        # im_fft2 = np.fft.fft2(img_original)

        r, c = im_fft2.shape
        print(im_fft2[10, 10])

        im_fft2[10, 10] = 0.0

        print(im_fft2[10, 10])
        print("checkpoint1")
        im_fft2[int(r * keep_fraction):int(r * (1 - keep_fraction)), :] = 0.0
        im_fft2[:, int(c * keep_fraction):int(c * (1 - keep_fraction))] = 0.0

        img_new = twoD_IFFT(im_fft2).real

        plt.figure("Mode_2")
        plt.subplot(121)
        plt.imshow(img_original)

        plt.subplot(122)
        plt.imshow(img_new)
        plt.show()

    if (mode == 3):
        print("mode 3 is triggered")
        threshold_19 = 2900
        threshold_38 = 5000
        threshold_57 = 8000
        threshold_76 = 13000
        threshold_95 = 42500

        im_fft2 = twoD_FFT(img_original)

        h, w = im_fft2.shape
        print("---------------------------")

        print("Image Pixels Number:", h * w)
        print("---------------------------------")
        # print(im_fft2.shape)

        # print(im_fft2[10, 10])

        # im_fft2[10,10] = 0.0

        # print(im_fft2[10, 10])
        # print("checkpoint2")
        num_0_19 = 0
        num_0_38 = 0
        num_0_57 = 0
        num_0_76 = 0
        num_0_95 = 0

        im_19 = twoD_FFT(img_original)

        for j in range(w):
            for i in range(h):
                if int(abs(im_19[i, j])) < threshold_19:
                    im_19[i, j] = complex(0, 0)
                    num_0_19 += 1

        im_38 = twoD_FFT(img_original)

        for j in range(w):
            for i in range(h):
                if int(abs(im_38[i, j])) < threshold_38:
                    im_38[i, j] = complex(0, 0)
                    num_0_38 += 1

        im_57 = twoD_FFT(img_original)

        for j in range(w):
            for i in range(h):
                if int(abs(im_57[i, j])) < threshold_57:
                    im_57[i, j] = complex(0, 0)
                    num_0_57 += 1

        im_76 = twoD_FFT(img_original)

        for j in range(w):
            for i in range(h):
                if int(abs(im_76[i, j])) < threshold_76:
                    im_76[i, j] = complex(0, 0)
                    num_0_76 += 1

        im_95 = twoD_FFT(img_original)

        for j in range(w):
            for i in range(h):
                if int(abs(im_95[i, j])) < threshold_95:
                    im_95[i, j] = complex(0, 0)
                    num_0_95 += 1

        # for j in range(w):
        #     for i in range(h):
        #         if int(abs(im_19[i, j])) < threshold_19:
        #             im_19[i, j] = complex(0, 0)
        #             num_0_19 += 1
        #         if int(abs(im_38[i, j])) < threshold_38:
        #             im_38[i, j] = complex(0, 0)
        #             num_0_38 += 1
        #         if int(abs(im_57[i, j])) < threshold_57:
        #             im_57[i, j] = complex(0, 0)
        #             num_0_57 += 1
        #         if int(abs(im_76[i, j])) < threshold_76:
        #             im_76[i, j] = complex(0, 0)
        #             num_0_76 += 1
        #         if int(abs(im_95[i, j])) < threshold_95:
        #             im_95[i, j] = complex(0, 0)
        #             num_0_95 += 1

        if not os.path.exists('matrix'):
            os.mkdir('matrix')

        savez_compressed('matrix/compressImage_19.npz', im_19)
        savez_compressed('matrix/compressImage_38.npz', im_38)
        savez_compressed('matrix/compressImage_57.npz', im_57)
        savez_compressed('matrix/compressImage_76.npz', im_76)
        savez_compressed('matrix/compressImage_95.npz', im_95)

        # homedir = os.path.expanduser("~")
        # cwd = os.getcwd()
        # pathset = os.path.join(homedir, "Desktop/gh/networksProjects/Assignment 2/matrix")

        # output_19 = "compressedImage_19.npz"

        # print("file is created1")

        # if not(os.path.exists(pathset)):
        #     os.makedirs(pathset, exist_ok=True)

        #     ds = {"ORE_MAX_GIORNATA": 5}
        #     # write the file in the new directory
        #     np.save(os.path.join(pathset, output_19), ds)

        im_i19 = twoD_IFFT(im_19).real
        im_i38 = twoD_IFFT(im_38).real
        im_i57 = twoD_IFFT(im_57).real
        im_i76 = twoD_IFFT(im_76).real
        im_i95 = twoD_IFFT(im_95).real

        print("Number of 0-coefficient-pixels")

        print("at 19% Compression Level:", num_0_19)
        print("at 38% Compression Level:", num_0_38)
        print("at 57% Compression Level:", num_0_57)
        print("at 76% Compression Level:", num_0_76)
        print("at 95% Compression Level:", num_0_95)

        print("---------------------------------")

        plt.figure("Mode_3")

        plt.subplot(231)
        plt.imshow(img_original)

        plt.subplot(232)
        plt.imshow(im_i19)

        plt.subplot(233)
        plt.imshow(im_i38)

        plt.subplot(234)
        plt.imshow(im_i57)

        plt.subplot(235)
        plt.imshow(im_i76)

        plt.subplot(236)
        plt.imshow(im_i95)

        plt.show()

    if mode == 4:
        print("mode 4 is triggered")
        # print(np.allclose(a, a2))
        # print(str(endTime-startTime) + " " + str(endTime2-startTime2))
        size = [32, 64, 128, 256, 512]

        dft_mean = list()
        dft_std = list()
        fft_mean = list()
        fft_std = list()

        x = 32
        for j in range(5):
            dft_list = list()
            for i in range(15):
                y = np.random.rand(x, x)
                startTime = time.perf_counter()
                twoD_DFT(y)
                endTime = time.perf_counter()
                # print(np.allclose(my, np.fft.fft2(y)))
                diffTime = endTime - startTime
                dft_list.append(diffTime)

            dft_mean.append(statistics.mean(dft_list))
            dft_std.append(statistics.stdev(dft_list))
            x *= 2

        x = 32
        for j in range(5):
            fft_list = list()
            for i in range(15):
                y = np.random.rand(x, x)
                startTime = time.perf_counter()
                twoD_FFT(y)
                endTime = time.perf_counter()
                # print(np.allclose(my, np.fft.fft2(y)))
                diffTime = endTime - startTime
                fft_list.append(diffTime)

            fft_mean.append(statistics.mean(fft_list))
            fft_std.append(statistics.stdev(fft_list))
            x *= 2

        plt.figure("Mode_4")
        plt.subplot(121)
        plt.plot(size, dft_mean, label="DFT")
        plt.plot(size, fft_mean, label="FFT")
        plt.xlabel('Size')
        plt.ylabel('Runtime Mean')
        plt.title('Mean')
        plt.legend()

        plt.subplot(122)
        plt.plot(size, dft_std, label="DFT")
        plt.plot(size, fft_std, label="FFT")
        plt.xlabel('Size')
        plt.ylabel('Runtime Std. Dev.')
        plt.title('Standard Deviation')
        plt.legend()
        plt.show()


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
