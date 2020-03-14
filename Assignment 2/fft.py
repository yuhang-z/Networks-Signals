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
        return np.concatenate([X_even + factor[:N / 2] * X_odd,
                               X_even + factor[N / 2:] * X_odd])


# TODO: this is a more efficient way of doing FFT. Have to choose which to use: this or FFT
def FFT_vectorized(x):
    """A vectorized, non-recursive version of the Cooley-Tukey FFT"""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]

    if np.log2(N) % 1 > 0:
        raise ValueError("size of x must be a power of 2")

    # N_min here is equivalent to the stopping condition above,
    # and should be a power of 2
    N_min = min(N, 32)

    # Perform an O[N^2] DFT on all length-N_min sub-problems at once
    n = np.arange(N_min)
    k = n[:, None]
    M = np.exp(-2j * np.pi * n * k / N_min)
    X = np.dot(M, x.reshape((N_min, -1)))

    # build-up each level of the recursive calculation all at once
    while X.shape[0] < N:
        X_even = X[:, :X.shape[1] / 2]
        X_odd = X[:, X.shape[1] / 2:]
        factor = np.exp(-1j * np.pi * np.arange(X.shape[0])
                        / X.shape[0])[:, None]
        X = np.vstack([X_even + factor * X_odd,
                       X_even - factor * X_odd])

    return X.ravel()




mode = 1
address = "moonlanding.png"

if __name__ == '__main__':
    # If there is no input or more than two inputs, exit
    if len(sys.argv) == 1 or len(sys.argv) > 3:
        print("Invalid inputs!\tpython fft.py [-m mode] [-i image]")
        exit(1)

    # Case 1: Two inputs: mode and address
    elif len(sys.argv) == 3:
        try:    # Is this a number?
            mode = int(sys.argv[1])
        except ValueError:
            print("Invalid mode input! Mode should be inputted 1, 2, 3, or 4!\tYour input: " + sys.argv[1])
            exit(1)
        else:   # Check if mode is in range of [1, 4]
            if not 1 <= mode <= 4:
                print("Invalid mode input! Mode should be inputted 1, 2, 3, or 4!\tYour input: " + sys.argv[1])
                exit(1)

        # Is this a valid address?
        if not os.path.isfile(sys.argv[2]):
            print("Invalid image input! Filename does not exist!\tYour input: " + sys.argv[2])
            exit(1)
        else:
            address = sys.argv[2]

    # One input: either mode or address
    else:
        try:    # Is this a number?
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




