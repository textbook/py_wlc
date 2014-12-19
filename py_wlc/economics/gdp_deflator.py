"""Provides conversion between nominal and real prices."""
from ..generic import ExtendedDict, IndexSeries


class GdpDeflator(IndexSeries):
    """

    If extension beyond the specified :py:attr:`~._rates` is required,
    the ``rates`` argument is replaced with an
    :py:class:`~.ExtendedDict`, such that the first and last rates are
    continued indefinitely. Otherwise, there is no growth outside the
    predefined data-set (i.e. assumed rate of ``0.0``).

    Arguments:
      base_year (``int``): The price base year to deflate to.
      rates (``dict`` of ``int``: ``str``): The annual rates.
      extend (``bool``, optional): Whether or not to extend the rates
        beyond the predefined data. Defaults to ``False``.

    """

    def __init__(self, base_year, rates, extend=False):
        if not rates:
            rates = {base_year: 0.0}
        rates = {year-base_year: rate for year, rate in rates.items()}
        if extend:
            rates = ExtendedDict(rates)
        super().__init__(base_year, rates, 100.0)

    def conversion_factor(self, year_from, year_to=None):
        """Calculate the factor to convert costs between two years.

        Arguments:
          year_from (``int``): The year to convert from.
          year_to (``int``, optional): The year to convert to. Defaults
            to :py:attr:`~.base_year`.

        Returns:
          float: The conversion factor between the two years.

        """
        if year_to is None:
            year_to = self.base_year
        return self.__getitem__(year_to) / self.__getitem__(year_from)

    def _extend_values(self, year):
        min_year = min(self._values)
        max_year = max(self._values)
        if year < min_year:
            for year_ in range(min_year-1, year-1, -1):
                fact = 1 + self._rates.get(year_, 0)
                self._values[year_] = self._values[year_+1] / fact
        elif year > max_year:
            for year_ in range(max_year, year):
                fact = 1 + self._rates.get(year_, 0)
                self._values[year_+1] = self._values[year_] * fact
