from limix.nice_arrays import normalise_phenotype_matrix
from limix.nice_arrays import normalise_covariates_matrix
from limix.nice_arrays import normalise_kinship_matrix

from pandas import DataFrame
from numpy.testing import assert_allclose, assert_equal
from numpy.random import RandomState
from numpy import newaxis, stack, dot, concatenate, arange


def test_nice_arrays_phenotype():

    random = RandomState(0)
    v = random.randn(5)
    y = [v.copy()]
    y += [v.copy()[:, newaxis]]
    y += [DataFrame(data=v.copy())]

    samples = ['sample{}'.format(i) for i in range(5)]
    data = stack([samples, v.copy()], axis=1)
    y += [DataFrame(data=data)]

    samples = ['sample{}'.format(i) for i in range(5)]
    data = stack([samples, v.copy()], axis=1)
    df = DataFrame(data=data)
    df = df.set_index(0)
    y += [df]

    for i, yi in enumerate(y):
        df = normalise_phenotype_matrix(yi, 'normal')
        assert_allclose(df.values, v[:, newaxis])
        assert_equal(df.shape[0], 5)
        assert_equal(df.shape[1], 1)


def test_nice_arrays_covariates():
    random = RandomState(0)
    v = random.randn(5)
    v0 = random.randn(5)

    M = [v.copy()]
    M += [v.copy()[:, newaxis]]
    M += [DataFrame(data=v.copy())]
    samples = ['sample{}'.format(i) for i in range(5)]
    M += [DataFrame(data=v.copy(), index=samples)]
    M += [DataFrame(data=v.copy(), columns=['0'])]
    M += [DataFrame(data=v.copy(), index=samples, columns=['0'])]

    for i, Mi in enumerate(M):
        df = normalise_covariates_matrix(Mi)
        assert_allclose(df.values, v[:, newaxis])
        assert_equal(df.shape[0], 5)
        assert_equal(df.shape[1], 1)


def test_nice_arrays_kinship():

    random = RandomState(0)
    X = random.randn(5, 10)
    K0 = dot(X, X.T)

    K = [K0.copy()]
    K += [DataFrame(data=K0.copy())]
    data = K0.copy()
    data = concatenate((arange(5)[:, newaxis], K0), axis=1)
    K += [DataFrame(data=data)]
    data = concatenate((arange(5)[newaxis, :], K0), axis=0)
    K += [DataFrame(data=data)]

    for i, Ki in enumerate(K):
        df = normalise_kinship_matrix(Ki)
        assert_allclose(df.values, K0)
        assert_equal(df.shape[0], 5)
        assert_equal(df.shape[1], 5)
