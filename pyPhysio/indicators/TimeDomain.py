# coding=utf-8
from __future__ import division

import numpy as _np

from ..BaseIndicator import Indicator as _Indicator
from ..filters.Filters import Diff as _Diff
from ..Utility import PhUI as _PhUI
from ..tools.Tools import Histogram


__author__ = 'AleB'


# class HistogramMax(_Indicator):
#     @classmethod
#     def algorithm(cls, signal, params):
#         """
#         Computes the size of the biggest Histogram bin
#         @return: (values, bins)
#         @rtype: (array, array)
#         """
#
#         h, b = Histogram(params)(signal)
#         return _np.max(h)


class Mean(_Indicator):
    """
    Compute the arithmetic mean along the specified axis, ignoring NaNs.

    Uses directly numpy.nanmean, but uses the PyPhysio cache.
    """

    @classmethod
    def algorithm(cls, data, params):
        return _np.nanmean(data.get_values())


class Min(_Indicator):
    """
    Return minimum of the data, ignoring any NaNs.

    Uses directly numpy.nanmin, but uses the PyPhysio cache.
    """

    @classmethod
    def algorithm(cls, data, params):
        return _np.nanmin(data.get_values())


class Max(_Indicator):
    """
    Return maximum of the data, ignoring any NaNs.

    Uses directly numpy.nanmax, but uses the PyPhysio cache.
    """

    @classmethod
    def algorithm(cls, data, params):
        return _np.nanmax(data.get_values())


class Range(_Indicator):
    """
    Computes the range value of the data, ignoring any NaNs.
    The range is the difference Max(d) - Min(d)
    """

    @classmethod
    def algorithm(cls, data, params):
        return Max()(data) - Min()(data)


class Median(_Indicator):
    """
    Computes the median of the data.

    Uses directly numpy.median but uses the PyPhysio cache.
    """

    @classmethod
    def algorithm(cls, data, params):
        return _np.median(data.get_values())


class StDev(_Indicator):
    """
    Computes the standard deviation of the data, ignoring any NaNs.

    Uses directly numpy.nanstd but uses the PyPhysio cache.
    """

    @classmethod
    def algorithm(cls, data, params):
        return _np.nanstd(data.get_values())


class Sum(_Indicator):
    """
    Computes the sum of the values in the data, treating Not a Numbers (NaNs) as zero.

    Uses directly numpy.nansum but uses the PyPhysio cache.
    """

    @classmethod
    def algorithm(cls, data, params):
        return _np.nansum(data.get_values())


class AUC(_Indicator):
    """
    Computes the Area Under the Curve of the data, treating Not a Numbers (NaNs) as zero.
    """
    #TODO: check that signal is Evenly
    @classmethod
    def algorithm(cls, data, params):
        fsamp = data.get_sampling_freq()
        return (1. / fsamp) * Sum()(data)


# HRV
class RMSSD(_Indicator):
    """
    Computes the square root of the mean of the squared 1st order discrete differences.
    """

    @classmethod
    def algorithm(cls, signal, params):
        diff = _Diff()(signal)
        return _np.sqrt(_np.mean(_np.power(diff.get_values(), 2)))


class SDSD(_Indicator):
    """
    Calculates the standard deviation of the 1st order discrete differences.
    """

    @classmethod
    def algorithm(cls, signal, params):
        diff = _Diff()(signal)
        return StDev()(diff)


class Triang(_Indicator):
    """
    Computes the HRV triangular index.
    """
    #TODO: check

    @classmethod
    def algorithm(cls, data, params):
        step = 1000. / 128
        min_ibi = _np.min(data)
        max_ibi = _np.max(data)
        if max_ibi - min_ibi / step + 1 < 10:
            cls.warn("len(bins) < 10")
            return _np.nan
        else:
            bins = _np.arange(min_ibi, max_ibi, step)
            h, b = Histogram(histogram_bins=bins)(data)
            return len(data) / _np.max(h)


class TINN(_Indicator):
    """
    Computes the triangular interpolation of NN interval histogram.
    """
    #TODO: check

    @classmethod
    def algorithm(cls, data, params):
        step = 1000. / 128
        min_ibi = _np.min(data)
        max_ibi = _np.max(data)
        if (max_ibi - min_ibi) / step + 1 < 10:
            cls.warn("len(bins) < 10")
            return _np.nan
        else:
            bins = _np.arange(min_ibi, max_ibi, step)
            h, b = Histogram(histogram_bins=bins)(data)
            max_h = _np.max(h)
            hist_left = _np.array(h[0:_np.argmax(h)])
            ll = len(hist_left)
            hist_right = _np.array(h[_np.argmax(h):])
            rl = len(hist_right)
            y_left = _np.array(_np.linspace(0, max_h, ll))

            minx = _np.Inf
            pos = 0
            for i in range(1, len(hist_left) - 1):
                curr_min = _np.sum((hist_left - y_left) ** 2)
                if curr_min < minx:
                    minx = curr_min
                    pos = i
                y_left[i] = 0
                y_left[i + 1:] = _np.linspace(0, max_h, ll - i - 1)

            n = b[pos - 1]

            y_right = _np.array(_np.linspace(max_h, 0, rl))
            minx = _np.Inf
            pos = 0
            for i in range(rl - 1, 1, -1):
                curr_min = _np.sum((hist_right - y_right) ** 2)
                if curr_min < minx:
                    minx = curr_min
                    pos = i
                y_right[i - 1] = 0
                y_right[0:i - 2] = _np.linspace(max_h, 0, i - 2)

            m = b[_np.argmax(h) + pos + 1]
            return m - n