"""Calculation methods for residual value of assets."""

from __future__ import division

from ..utils import memo

@memo
def sum_of_years_digits(year):
    """Calculate the sum of years' digits.

    Arguments:
      year (int): The year to calculate up to.

    Returns:
      int: The sum of years' digits.

    """
    if year <= 0:
        return 0
    return year + sum_of_years_digits(year-1)


class ResidualValueCalculator(object):
    """A calculator to generate residual values of assets.

    Arguments:
      method (``str``): The method to use for the calculation (must be
        in :py:attr:`METHODS`, see `Wikipedia`_ for method details).

    Raises:
      ValueError: If ``method`` is not in :py:attr:`METHODS`.

    .. _`Wikipedia`:
       http://en.wikipedia.org/wiki/Depreciation#Methods_of_depreciation

    """

    METHODS = {"linear": "linear",
               "double-declining": "double_declining",
               "sum of years' digits": "sum_of_years"}

    def __init__(self, method):
        if method not in self.METHODS:
            raise ValueError("Not a valid method: {!r}.".format(method))
        self._method = method
        self.func = getattr(self, self.METHODS[method])

    @property
    def method(self):
        """The current method for residual value calculations.

        Returns:
          str: The name of the current method (read-only).

        """
        return self._method

    def calculate(self, value, life, build_year, target_year, scrap_value=0.0):
        """Calculate residual value, using selected :py:attr:`method`.

        Notes:
          Residual value is assumed to be the ``scrap_value`` after the
          life expires (``build_year + life``). The residual value is
          never allowed to fall below the ``scrap_value``.

        Arguments:
          value (``float``): The initial asset value.
          life (``int``): The life of the asset, in years.
          build_year (``int``): The year in which the asset is built.
          target_year (``int``): The year in which to calculate the
            asset's residual value.
          scrap_value (``float``, optional): The asset's value after
            life expiry. Defaults to 0.0.

        Returns:
          float: The calculated residual value.

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
        return max(scrap_value,
                   self.func(value, life, build_year,
                             target_year, scrap_value))

    @classmethod
    def available_methods(cls):
        """Show the methods available in :py:attr:`METHODS`.

        Returns:
          ``list`` of ``str``: The available methods.

        """
        return list(cls.METHODS.keys())

    @staticmethod
    def double_declining(value, life, build_year, target_year, scrap_value):
        """Calculate residual value with double-declining method.

        Notes:
          The double-declining method, a specific `declining balance`_
          method, assumes that the same proportion of the remaining
          value is lost in each year of the asset's life. In this case,
          the proportion is double the proportion lost in each year
          under the :py:meth:`linear` method.

        Arguments:
          value (``float``): The initial asset value.
          life (``int``): The life of the asset, in years.
          build_year (``int``): The year in which the asset is built.
          target_year (``int``): The year in which to calculate the
            asset's residual value.
          scrap_value (``float``): The asset's value after life expiry.

        Returns:
          float: The calculated residual value.

        .. _`declining balance`:
           http://en.wikipedia.org/wiki/Depreciation#Declining_Balance_Method

        """
        _ = scrap_value
        return value * (1 - (2 * (1 / life))) ** (target_year - build_year)

    @staticmethod
    def linear(value, life, build_year, target_year, scrap_value):
        """Calculate residual value with linear (straight-line) method.

        Notes:
          The linear (or `straight-line depreciation`_) method assumes
          that the same amount of the asset's value is lost in every
          year of its life.

        Arguments:
          value (``float``): The initial asset value.
          life (``int``): The life of the asset, in years.
          build_year (``int``): The year in which the asset is built.
          target_year (``int``): The year in which to calculate the
            asset's residual value.
          scrap_value (``float``): The asset's value after life expiry.

        Returns:
          float: The calculated residual value.

        .. _`straight-line depreciation`:
           http://en.wikipedia.org/wiki/Depreciation#Straight-line_depreciation

        """
        fact = 1 - ((target_year - build_year) / life)
        return ((value - scrap_value) * fact) + scrap_value

    @staticmethod
    def sum_of_years(value, life, build_year, target_year, scrap_value):
        """Calculate residual value with sum of years' digits method.

        Notes:
          The `sum of years' digits`_ method uses a "schedule of
          fractions" to depreciate the value, based on summing the
          digits of all years in the life for the denominator.

        Arguments:
          value (``float``): The initial asset value.
          life (``int``): The life of the asset, in years.
          build_year (``int``): The year in which the asset is built.
          target_year (``int``): The year in which to calculate the
            asset's residual value.
          scrap_value (``float``): The asset's value after life expiry.

        Returns:
          float: The calculated residual value.

        .. _`sum of years' digits`:
           http://en.wikipedia.org/wiki/Depreciation#Sum-of-years-digits_method

        """
        res_life = life - (target_year - build_year)
        fact = ((sum_of_years_digits(life) - sum_of_years_digits(res_life)) /
                sum_of_years_digits(life))
        return scrap_value + ((value - scrap_value) * (1 - fact))



