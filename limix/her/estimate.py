from __future__ import division

from numpy import pi, var, ones
from numpy import asarray as npy_asarray

from glimix_core.glmm import GLMMExpFam
from glimix_core.lmm import LMM
from numpy_sugar.linalg import economic_qs

from ..fprint import oprint
from ..nice_arrays import (covariates_process, named_to_unamed_matrix,
                           phenotype_process)
from ..qc import gower_norm
from ..util import Timer
from ..util.npy_dask import asarray
from ..likelihood import normalise_extreme_values


def estimate(y, lik, K, M=None, verbose=True):
    r"""Estimate the so-called narrow-sense heritability.

    It supports Normal, Bernoulli, Binomial, and Poisson phenotypes.
    Let :math:`N` be the sample size and :math:`S` the number of covariates.

    Parameters
    ----------
    y : tuple, array_like
        Either a tuple of two arrays of `N` individuals each (Binomial
        phenotypes) or an array of `N` individuals (Normal, Poisson, or
        Bernoulli phenotypes). It does not support missing values yet.
    lik : {'normal', 'bernoulli', 'binomial', 'poisson'}
        Sample likelihood describing the residual distribution.
    K : array_like
        `N` by `N` covariance matrix (e.g., kinship coefficients).
    M : array_like, optional
        `N` individuals by `D` covariates.
        By default, ``M`` is a (`N`, `1`) array of ones.
    verbose : bool, optional
        if ``True``, details such as runtime are displayed.

    Returns
    -------
    float
        Estimated heritability.

    Examples
    --------
    .. doctest::

        >>> from numpy import dot, exp, sqrt
        >>> from numpy.random import RandomState
        >>> from limix.her import estimate
        >>>
        >>> random = RandomState(0)
        >>>
        >>> G = random.randn(150, 200) / sqrt(200)
        >>> K = dot(G, G.T)
        >>> z = dot(G, random.randn(200)) + random.randn(150)
        >>> y = random.poisson(exp(z))
        >>>
        >>> print('%.2f' % estimate(y, 'poisson', K, verbose=False))
        0.18
    """

    if verbose:
        lik_name = lik.lower()
        lik_name = lik_name[0].upper() + lik_name[1:]
        analysis_name = "Heritability estimation"
        oprint("*** %s using %s-GLMM ***" % (analysis_name, lik_name))

    if isinstance(y, (tuple, list)):
        y = npy_asarray(y, float).T

    if M is None:
        M = ones((y.shape[0], 1))

    y = phenotype_process(lik, y)
    normalise_extreme_values(y, lik)

    K = asarray(K)
    M = covariates_process(M, K.shape[0])
    K = gower_norm(K)

    desc = "Eigen decomposition of the covariance matrix..."
    with Timer(desc=desc, disable=not verbose):
        QS = economic_qs(K)

    lik = lik.lower()
    M = named_to_unamed_matrix(M)
    y = _binomial_y(y.values, lik)

    if lik == 'normal':
        method = LMM(y, M, QS)
        method.fit(verbose=verbose)
    else:
        method = GLMMExpFam(y, lik, M, QS, n_int=500)
        method.fit(verbose=verbose, factr=1e6, pgtol=1e-3)

    g = method.scale * (1 - method.delta)
    e = method.scale * method.delta
    if lik == 'bernoulli':
        e += pi * pi / 3

    if lik == 'normal':
        v = method.fixed_effects_variance
    else:
        v = var(method.mean())

    return g / (v + g + e)


def _binomial_y(y, lik):
    if lik == 'binomial':
        return y[:, 0], y[:, 1]
    return y.ravel()
