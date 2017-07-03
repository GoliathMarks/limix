from __future__ import division

from glimix_core.glmm import GLMM
from glimix_core.lmm import LMM
from numpy import ascontiguousarray, copy, ones, var
from numpy import asarray as npy_asarray
from numpy_sugar.linalg import economic_qs

from limix.util import Timer, asarray
from limix.stats.kinship import gower_norm
from ..covariates import assure_named_covariates, named_covariates_to_array


def estimate(y, lik, K, M=None, verbose=True):
    r"""Estimate the so-called narrow-sense heritability.

    It supports Normal, Bernoulli, Binomial, and Poisson phenotypes.
    Let :math:`N` be the sample size and :math:`S` the number of covariates.

    Parameters
    ----------
    y : (tuple, array_like)
        Either a tuple of two arrays of `N` individuals each (Binomial
        phenotypes) or an array of `N` individuals (Normal, Poisson, or
        Bernoulli phenotypes). It does not support missing values yet.
    lik : {'normal', 'bernoulli', 'binomial', 'poisson'}
        Sample likelihood describing the residual distribution.
    K : array_like
        `N` by `N` covariance matrix (e.g., kinship coefficients).
    M : (array_like, optional)
        `N` individuals by `D` covariates.
        By default, ``M`` is a (`N`, `1`) array of ones.
    verbose : (bool, optional)
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
        >>> from limix.heritability import estimate
        >>>
        >>> random = RandomState(0)
        >>>
        >>> G = random.randn(50, 100)
        >>> K = dot(G, G.T)
        >>> z = dot(G, random.randn(100)) / sqrt(100)
        >>> y = random.poisson(exp(z))
        >>>
        >>> print('%.2f' % estimate(y, 'poisson', K, verbose=False))
        0.70
    """

    if verbose:
        lik_name = lik.lower()
        lik_name = lik_name[0].upper() + lik_name[1:]
        analysis_name = "Heritability estimation"
        print("*** %s using %s-GLMM ***" % (analysis_name, lik_name))

    K = asarray(K)
    M = assure_named_covariates(M, K.shape[0])
    K = gower_norm(K)

    if isinstance(y, (tuple, list)):
        y = tuple([npy_asarray(p, float) for p in y])
    else:
        y = npy_asarray(y, float)

    desc = "Eigen decomposition of the covariance matrix..."
    with Timer(desc=desc, disable=not verbose):
        QS = economic_qs(K)

    lik = lik.lower()

    if lik == 'normal':
        raise NotImplementedError
    else:
        glmm = GLMM(y, lik, named_covariates_to_array(M), QS)
        glmm.feed().maximize(progress=verbose)

    g = glmm.scale * (1 - glmm.delta)
    e = glmm.scale * glmm.delta
    h2 = g / (var(glmm.mean()) + g + e)

    return h2
