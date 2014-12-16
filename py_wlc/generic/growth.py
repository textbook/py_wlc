"""Generic functionality for modelling growth series."""


class IndexSeries(object):

    """Growth rates and factors for indexation series.

    Notes:
      The ``_rates`` dictionary is fully-populated at initialisation,
      but the ``_values`` dictionary is filled lazily - values are only
      calculated as needed.

      The class supports a ``Mapping``-like interface; factors can be
      accessed with ``value = growth_rate[year]`` or ``value =
      growth_rate.get(year, default)``.

    Note:
      The term 'relative year' refers to the year relative to
      ``year_zero`` e.g. ``3``. The term 'absolute year' refers to a
      calendar year, e.g. ``2013``. Relative years are used internally,
      absolute years for the external interface.

    Arguments:
      base_year (``int``): the year in which the value is equal to the
        ``initial_value``
      rates (``dict`` of ``int``: ``float``): the growth rates to use,
        keyed by relative year
      initial_value (``float``): the first value for the output series.
      year_zero (``int``): the zeroth year for accessing growth rates.
      initial_rate (``float``, optional): the rate to use for years
        prior to the first year in the ``rates`` dictionary

    Attributes:
      base_year (``int``): The base year for discounting, i.e. the year
        in which the value is the ``initial_value``.
      year_zero (``int``): The zeroth year for growth, i.e. the year
        from which the rates are selected from ``_rates``.
      _rates (``dict`` of ``int``: ``float``): The growth rates, where
        the key is the relative start year and the value is the rate to
        apply.
      _initial_rate (``float``): The growth rate corresponding to the
        first year in the ``rates`` dictionary.
      _final_rate (``float``): The growth rate corresponding to the
        last year in the ``rates`` dictionary.
      _values (``dict`` of ``int``: ``float``): The values, keyed by
        year.

    """
    def __init__(self, base_year, rates, initial_value,
                 year_zero=None, initial_rate=None):
        self.base_year = base_year
        self._rates = rates.copy()
        if year_zero is None:
            year_zero = base_year
        self.year_zero = year_zero
        self._rates = rates.copy()
        if initial_rate is None:
            initial_rate = rates[min(rates)]
        self._initial_rate = initial_rate
        self._final_rate = rates[max(rates)]

        min_year = min(rates)
        max_year = max(rates)
        rate = initial_rate
        for year in range(min_year, max_year):
            if year in rates:
                rate = rates[year]
            else:
                self._rates[year] = rate

        self._values = {base_year-year_zero: initial_value}
        self._extend_values(0)

        self._hash = None

    def __getitem__(self, year):
        year -= self.year_zero
        if year not in self._values:
            self._extend_values(year)
        return self._values[year]

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __hash__(self):
        if self._hash is None:
            self._hash = (hash(self.base_year) ^
                          hash(self.year_zero) ^
                          hash(frozenset(self._rates.items())))
        return self._hash

    def __eq__(self, other):
        # pylint: disable=protected-access
        return (self.base_year == other.base_year and
                self.year_zero == other.year_zero and
                self._rates == other._rates)

    def get(self, year, default=None):
        """Retrieve value or supplied default for given year.

        Arguments:
          year (int): The year to retrieve the value for.
          default (float or None, optional): The value to return if
            retrieval fails. Defaults to ``None``.

        Returns:
          float or None: The retrieved or ``default`` value.

        """
        try:
            self.__getitem__(year)
        except KeyError:
            return default

    def rate(self, year):
        """The rate used in the specified year.

        Arguments:
          year (int): The year to retrieve the rate for.

        Returns:
          float: The rate used in that year.

        """
        try:
            return self._rates[year]
        except KeyError:
            if year < min(self._rates):
                return self._initial_rate
            return self._final_rate

    def _extend_values(self, year):
        """Extend the values dictionary to cover the specified year."""
        raise NotImplementedError
