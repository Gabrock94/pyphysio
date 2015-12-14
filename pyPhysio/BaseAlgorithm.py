# coding=utf-8
__author__ = 'AleB'


class Algorithm(object):
    """
    This is the algorithm container super class. It should be used only to be extended.
    """

    def __init__(self, params=None, _kwargs=None, **kwargs):
        """
        Incorporates the parameters and saves them in the instance.
        @param params: Dictionary of string-value parameters passed by the user.
        @type params: dict
        @param _kwargs: Internal channel for subclasses kwargs parameters.
        @type _kwargs: dict
        @param kwargs: kwargs parameters to pass to the feature extractor.
        @type kwargs: dict
        """
        assert self.__class__ != Algorithm, "This class is abstract and must be extended to be used."
        assert params is None or type(params) is dict
        assert type(_kwargs) is dict or _kwargs is None
        if params is None:
            self._params = {}
        else:
            self._params = params.copy()
        self._params.update(kwargs)
        if type(_kwargs) is dict:
            self._params.update(_kwargs)

    def __call__(self, data):
        """
        Executes the algorithm using the parameters saved by the constructor.
        @param data: The data.
        @type data: TimeSeries
        @return: The result.
        """
        return self.get(data, self._params)

    def __repr__(self):
        return self.__class__.__name__ + str(self._params)

    @classmethod
    def get(cls, data, params=None, use_cache=True, **kwargs):
        """
        Gets the data from the cache or calculates, caches and returns it.
        @param data: Source data
        @type data: TimeSeries
        @param params: Parameters for the calculator
        @type params: dict
        @param use_cache: Weather to use the cache memory or not
        @type use_cache: bool
        @return: The value of the feature.
        """
        assert type(data) is TimeSeries, "The data must be a pandas TimeSeries."
        if type(params) is dict:
            kwargs.update(params)
        if use_cache is True:
            Cache.cache_check(data)
            return Cache.cache_get_data(data, cls, kwargs)
        else:
            return cls.algorithm(data, kwargs)

    @classmethod
    def cache_hash(cls, params):
        """
        This method gives an hash to use as a part of the key in the cache starting from the parameters used by the
        feature. Uses the method _utility_hash([par1,...parN])
        This class is abstract.
        @return: The hash of the parameters used by the feature.
        """
        p = params.copy()
        p.update({'': str(cls)})
        return cls._utility_hash(p)

    @staticmethod
    def _utility_hash(x):
        return str(x).replace('\'', '')

    @classmethod
    def algorithm(cls, data, params):
        """
        Placeholder for the subclasses
        @raise NotImplementedError: Ever
        """
        raise NotImplementedError(cls.__name__ + " is not implemented.")

    @classmethod
    def get_used_params(cls):
        """
        Placeholder for the subclasses
        @raise NotImplementedError: Ever
        """
        raise NotImplementedError(cls.__name__ + " is not implemented.")

    def get_params(self):
        """
        Placeholder for the subclasses
        @return
        """
        return self._params


class Cache(object):
    """ Class that gives a cache support. Uses Feature."""

    def __init__(self):
        pass

    # Field-checked methods

    @staticmethod
    def cache_clear(self):
        """
        Clears the cache and frees memory (GC?)
        """
        setattr(self, "_cache", {})

    @staticmethod
    def cache_check(self):
        """
        Checks the presence of the cache structure.
        """
        if not hasattr(self, "_cache"):
            Cache.cache_clear(self)

    # Field-unchecked methods

    @staticmethod
    def cache_invalidate(self, calculator, params):
        """
        Invalidates the specified calculator's cached data if any.
        @type calculator: Algorithm
        """
        hh = calculator.cache_hash(params)
        if hh in self._cache:
            del self._cache[hh]

    @staticmethod
    def cache_get_data(self, calculator, params):
        """
        Gets data from the cache if valid
        @type calculator: Algorithm
        @return: The data or None
        """
        hh = calculator.cache_hash(params)
        if hh not in self._cache:
            self._cache[hh] = calculator.algorithm(self, params)
        return self._cache[hh]