def get_shape(x):
    from . import dask

    if dask.is_array(x) or dask.is_dataframe(x):
        return _get_dask_shape(x)
    return x.shape


def _get_dask_shape(x):
    import dask.array as da

    return da.compute(*x.shape)


def vec(x):
    from numpy import reshape

    return reshape(x, (-1,) + x.shape[2:], order="F")


def unvec(x, shape):
    from numpy import reshape

    return reshape(x, shape, order="F")
