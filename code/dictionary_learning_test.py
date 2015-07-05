"""
    @Stan
    StochasticDictionaryLearningTest

    This script is made for comparing our implementation of DictionaryLearning
    algorithm and scikit learn's one.

    TODO:
    - test on sklearn example and compare it
    - think about class organisation
    - fix coding/writting conventions problem
    - create a function to run scikit's algo and store results
    - create a function to run our algo and store results
    - create a function to display results for both algorithm
        => display pictures
        => display running time, number of iterations...
        => display performances (how to measure it ?)
    - reproduce scikit's results with our implementation
    - try to do better with incorporating SQN, and proximal methods

    DONE:
    - load data
    - reconstruct data
    - run algorithm

    STRATEGY:
    1) Learn dictionary with both algorithm
    2) Plots dictionaries
    3) Use dictionaries to reconstruct images
    4) Plot images
    5) Measure differences

"""
from DictLearning.dictionary_learning import StochasticDictionaryLearning
from sqndict import SqnDictionaryLearning
from sklearn.feature_extraction.image import reconstruct_from_patches_2d
from sklearn.linear_model import OrthogonalMatchingPursuit
import numpy as np
from time import time
import matplotlib.pyplot as plt
from sklearn.feature_extraction.image import extract_patches_2d
from scipy.misc import lena


def learn_dictionaries(data, n_components=100, option=None,
                       alpha=0.001, n_iter=30, eta=100, verbose=0):
    '''
    Learn dictionaries with both methods
    INPUTS : dictionaries parameters
    - n_components
    - option, select SQN method or normal method
    - l, regularization parameter
    - n_iter, int, number of iterations
    - eta, int, mini batch size
    - verbose, int, control verbosity of algorithm

    OUTPUTS :
    - D_us
    - D_sklearn
    '''

    d_us = StochasticDictionaryLearning(n_components=100,
                                        option=None,
                                        alpha=0.001,
                                        n_iter=30,
                                        eta=100,
                                        verbose=0)

    d_sklearn = MiniBatchDictionaryLearning(n_components=100,
                                            alpha=1,
                                            n_iter=500,
                                            batch_size=3)


def plot_dictionary(D, dt=0, ld=0):
    '''
    Plots the dictionary
    '''

    patch_size = (7, 7)

    # dico is in a matrix, not in a list
    plt.figure(figsize=(4.2, 4))
    for i in range(0, len(D[0, :])):
        comp = D[:, i]
        plt.subplot(10, 10, i + 1)
        plt.imshow(comp.reshape(patch_size), cmap=plt.cm.gray_r,
                   interpolation='nearest')
        plt.xticks(())
        plt.yticks(())
    plt.suptitle('Dictionary learned from Lena patches\n' +
                 'Train time %.1fs on %d patches' % (dt, ld),
                 fontsize=16)
    plt.subplots_adjust(0.08, 0.02, 0.92, 0.85, 0.08, 0.23)
    # plt.show()


def show_with_diff(image, reference, title):
    '''
    Helper function to display denoising
    '''

    plt.figure(figsize=(5, 3.3))
    plt.subplot(1, 2, 1)
    plt.title('Image')
    plt.imshow(image, vmin=0, vmax=1,
               cmap=plt.cm.gray, interpolation='nearest')
    plt.xticks(())
    plt.yticks(())
    plt.subplot(1, 2, 2)
    difference = image - reference

    plt.title('Difference (norm: %.2f)' % np.sqrt(np.sum(difference ** 2)))
    plt.imshow(difference, vmin=-0.5, vmax=0.5, cmap=plt.cm.PuOr,
               interpolation='nearest')
    plt.xticks(())
    plt.yticks(())
    plt.suptitle(title, size=16)
    plt.subplots_adjust(0.02, 0.02, 0.98, 0.79, 0.02, 0.2)


def preprocess_data(lena):
    '''
    code from sklearn application of dictionary learning

    OUTPUTS:
    - data: n_patches, dim_patch array like. collection of patches
    - lena: original array updated/modified
    - distorted: right half of the image distorted
    '''

    lena = lena() / 256.0

    # downsample for higher speed
    lena = lena[::2, ::2] + lena[1::2, ::2] + lena[::2, 1::2] + lena[1::2, 1::2]
    lena /= 4.0
    height, width = lena.shape

    # Distort the right half of the image
    print('Distorting image...')
    distorted = lena.copy()
    distorted[:, height // 2:] += 0.075 * np.random.randn(width, height // 2)

    # Extract all reference patches from the left half of the image
    print('Extracting reference patches...')
    t0 = time()
    patch_size = (7, 7)
    data = extract_patches_2d(distorted[:, :height // 2], patch_size)
    data = data.reshape(data.shape[0], -1)
    data -= np.mean(data, axis=0)
    data /= np.std(data, axis=0)
    print('done in %.2fs.' % (time() - t0))

    return data, lena, distorted


def postprocess_data(lena):
    '''
    code from sklearn application of dictionary learning

    OUTPUTS:
    - data: noisy patches extracted from the right half of the image
    - intercept
    '''

    height, width = lena.shape

    # Distort the right half of the image
    print('Distorting image...')
    distorted = lena.copy()
    distorted[:, height // 2:] += 0.075 * np.random.randn(width, height // 2)

    print('Extracting noisy patches... ')
    t0 = time()
    patch_size = (7, 7)
    data = extract_patches_2d(distorted[:, height // 2:], patch_size)
    data = data.reshape(data.shape[0], -1)
    intercept = np.mean(data, axis=0)
    data -= intercept
    print('done in %.2fs.' % (time() - t0))

    return data, intercept


if __name__ == '__main__':
    '''
    Testing and correcting StochasticDictionaryLearning
    '''

    # create sdl object
    sdl = StochasticDictionaryLearning(n_components=100,
                                       option=None,
                                       alpha=1.0,
                                       n_iter=500,
                                       max_iter=10,
                                       batch_size=10,
                                       verbose=10)

    sdl = SqnDictionaryLearning(n_components=50,
                                option=None,
                                alpha=1.0,
                                n_iter=1,
                                max_iter=10,
                                batch_size=10,
                                verbose=10)

    # loads data
    data, lena, distorted = preprocess_data(lena)
    sdl.fit(data)

    # takes dictionary
    D = sdl.components

    # plots dictionary
    plot_dictionary(D)

    # post process data
    data, intercept = postprocess_data(lena)

    from sklearn.decomposition.dict_learning import sparse_encode

    t0 = time()
    title = 'first try'
    reconstructions = lena.copy()

    # encode noisy patches with learnt dictionary
    code = sparse_encode(data, D.T, gram=None,
                         cov=None, algorithm='omp',
                         n_nonzero_coefs=None, alpha=None,
                         copy_cov=True, init=None,
                         max_iter=1000, n_jobs=1)

    patch_size = (7, 7)
    height, width = lena.shape

    patches = np.dot(code, D.T)
    patches += intercept
    patches = patches.reshape(len(data), *patch_size)

    # reconstruct noisy image
    reconstructions[:, height // 2:] = reconstruct_from_patches_2d(
        patches, (width, height // 2))

    dt = time() - t0
    print('done in %.2fs.' % dt)

    # show the difference
    show_with_diff(distorted, lena, 'Distorted image')
    show_with_diff(reconstructions, lena,
                   title + ' (time: %.1fs)' % dt)
    plt.show()