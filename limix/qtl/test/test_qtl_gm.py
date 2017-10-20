from __future__ import division

from numpy import dot, zeros
from numpy.random import RandomState
from numpy.testing import assert_allclose

from limix.qtl import scan


def test_qtl_gmm_binomial():
    random = RandomState(0)
    nsamples = 50

    X = random.randn(nsamples, 2)
    ntrials = random.randint(1, nsamples, nsamples)
    z = dot(X, random.randn(2))

    successes = zeros(len(ntrials), int)
    for i in range(len(ntrials)):
        for _ in range(ntrials[i]):
            successes[i] += int(z[i] + 0.5 * random.randn() > 0)

    y = (successes, ntrials)

    lmm = scan(X, y, 'binomial', verbose=False)
    pv = lmm.variant_pvalues
    assert_allclose(pv, [3.801040e-01, 1.667984e-21], rtol=1e-5, atol=1e-5)