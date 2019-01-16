import numpy as np


def wp(data, wt, percentiles):
    """Compute weighted percentiles.
    If the weights are equal, this is the same as normal percentiles.
    Elements of the C{data} and C{wt} arrays correspond to
    each other and must have equal length (unless C{wt} is C{None}).
    @param data: The data.
    @type data: A L{np.ndarray} array or a C{list} of numbers.
    @param wt: How important is a given piece of data.
    @type wt: C{None} or a L{np.ndarray} array or a C{list} of numbers.
            All the weights must be non-negative and the sum must be
            greater than zero.
    @param percentiles: what percentiles to use.  (Not really percentiles,
            as the range is 0-1 rather than 0-100.)
    @type percentiles: a C{list} of numbers between 0 and 1.
    @rtype: [ C{float}, ... ]
    @return: the weighted percentiles of the data.
    """
    assert np.greater_equal(
        percentiles, 0.0).all(), "Percentiles less than zero"
    assert np.less_equal(percentiles, 1.0).all(
    ), "Percentiles greater than one"
    data = np.asarray(data)
    assert len(data.shape) == 1
    if wt is None:
        wt = np.ones(data.shape, np.float)
    else:
        wt = np.asarray(wt, np.float)
        assert wt.shape == data.shape
        assert np.greater_equal(wt, 0.0).all(
        ), "Not all weights are non-negative."
    assert len(wt.shape) == 1
    n = data.shape[0]
    assert n > 0
    i = np.argsort(data)
    sd = np.take(data, i, axis=0)
    sw = np.take(wt, i, axis=0)
    aw = np.add.accumulate(sw)
    if not aw[-1] > 0:
        raise ValueError("Nonpositive weight sum")
    w = (aw - 0.5 * sw) / aw[-1]
    spots = np.searchsorted(w, percentiles)
    o = []
    for (s, p) in zip(spots, percentiles):
        if s == 0:
            o.append(sd[0])
        elif s == n:
            o.append(sd[n - 1])
        else:
            f1 = (w[s] - p) / (w[s] - w[s - 1])
            f2 = (p - w[s - 1]) / (w[s] - w[s - 1])
            assert f1 >= 0 and f2 >= 0 and f1 <= 1 and f2 <= 1
            assert abs(f1 + f2 - 1.0) < 1e-6
            o.append(sd[s - 1] * f1 + sd[s] * f2)
    return o


def wtd_median(data, wt):
    """The weighted median is the point where half the weight is above
    and half the weight is below.   If the weights are equal, this is the
    same as the median.   Elements of the C{data} and C{wt} arrays correspond
    to each other and must have equal length (unless C{wt} is C{None}).

    @param data: The data.
    @type data: A L{numpy.ndarray} array or a C{list} of numbers.
    @param wt: How important is a given piece of data.
    @type wt: C{None} or a L{numpy.ndarray} array or a C{list} of numbers.
            All the weights must be non-negative and the sum must be
            greater than zero.
    @rtype: C{float}
    @return: the weighted median of the data.
    """
    spots = wp(data, wt, [0.5])
    assert len(spots) == 1
    return spots[0]


def sample_proportional_to_capacity(agents):
    caps = list(map(lambda a: a.capacity, agents))
    weight_sum = sum(caps)
    distribution = [1.0 * i / weight_sum for i in caps]
    leader_index = np.random.choice(
        np.arange(0, len(caps)), p=distribution)
    return agents[leader_index]
