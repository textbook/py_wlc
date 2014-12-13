"""Calculation methods for residual value of assets."""
from __future__ import division

from ..utils import memo

@memo
def sum_of_years(year):
    if year <= 0:
        return 0
    return year + sum_of_years(year-1)


def _double_declining(value, life, build_year, target_year, scrap_value):
    book_value = value
    rate = 2 * (1 / life)
    for year in range(target_year-build_year):
        book_value *= (1 - rate)
    return max(scrap_value, book_value)


def _linear(value, life, build_year, target_year, scrap_value):
    return ((value - scrap_value) *
            (1 - ((target_year - build_year) /
                  life))) + scrap_value


def _sum_of_years(value, life, build_year, target_year, scrap_value):
    res_life = life - (target_year - build_year)
    fact = (sum_of_years(life) - sum_of_years(res_life)) / sum_of_years(life)
    return scrap_value + ((value - scrap_value) * (1 - fact))


class ResidualValueCalculator(object):
    """A calculator to generate residual values of assets.

    Arguments:
      method (``str``): The method to use for the calculation (must be
        in :py:attr:`METHODS`).

    Attributes:
      method (``str``, read-only): The currently-selected method.

    Raises:
      ValueError: If ``method`` is not in :py:attr:`METHODS`.

    """

    METHODS = {'linear': _linear,
               'double-declining': _double_declining,
               "sum of years' digits": _sum_of_years}

    def __init__(self, method):
        if method not in self.METHODS:
            raise ValueError("Not a valid method: {!r}.".format(method))
        self._method = method

    @property
    def method(self):
        return self._method

    @classmethod
    def available_methods(cls):
        """Show the methods available in :py:attr:`METHODS`.

        Returns:
          ``list`` of ``str``: The available methods.

        """
        return cls.METHODS.keys()

    def calculate(self, value, life, build_year, target_year, scrap_value=0.0):
        """Calculate residual value, using selected :py:attr:`method`.

        Notes:
          Residual value is assumed to be the ``scrap_value`` after the
             life expires (``build_year + life``).

        Arguments:
          value (``float``): The initial asset value.
          life (``int``): The life of the asset, in years.
          build_year (``int``): The year in which the asset is built.
          target_year (``int``): The year in which to calculate the
            asset's residual value.
          scrap_value (``int``, optional): The asset's value after life
            expiry. Defaults to 0.0.

        Raises:
          ValueError: If ``target_year`` precedes the ``build_year``.

        """
        if target_year < build_year:
            msg = "Cannot calculate residual value prior to build."
            raise ValueError(msg)
        if target_year == build_year:
            return value
        if target_year > build_year + life:
            return scrap_value
        return self.METHODS[self._method](value, life, build_year,
                                          target_year, scrap_value)



