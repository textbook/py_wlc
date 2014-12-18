"""Representation of cost objects in various bases and forms."""
from __future__ import division


class Cost(object):
    """Represents costs and holds data for type conversions.

    The ``type_`` of a cost is necessary for conversion between the
    different types; costs can be provide in real or nominal terms and
    as a factor (or "resource") cost or a market price. Additionally, a
    cost can be a Present Value (discounted real market price).

    It is essential for an accurate calculation that the appropriate
    cost type is used for conversion to consistent output values.

    Note:
      The default assumptions for ``type_`` are :py:attr:`NOMINAL` and
      :py:attr:`FACTOR_COST`. For example::

          Cost(100, Cost.REAL, ...)

      is equivalent to::

          Cost(100, Cost.REAL | Cost.FACTOR_COST, ...)

      The exception is :py:attr:`PRESENT_VALUE`, which becomes a real
      market price once the discounting is factored out.

    Arguments:
      value (``float``): The value of the cost.
      type_ (``int``): The type of the cost.
      year (``int``): The year in which the cost is incurred.
      discount (:py:class:`~.Discount`): The discount factors to use
        for conversion to Present Value.
      deflator (:py:class:`~.GdpDeflator`): The GDP deflator factors to
        use for conversion to real prices.
      adjustment_factor (``float``): The factor to use for conversion
        to market prices.

    Attributes:
      cost (``float``): The nominal factor cost.
      year (``int``): The year in which the cost is incurred.
      discount_factor (``float``): The factor for conversion to Present
        Value (from real market prices).
      deflation_factor (``float``): The factor for conversion to real
        prices (from nominal prices).
      adjustment_factor (``float``): The factor for conversion to
        market prices (from factor costs).

    Raises:
      ValueError: If the ``type_`` argument is invalid.

    """

    FACTOR_COST = 1
    """Factor cost, excluding taxation."""
    RESOURCE_COST = 1
    """Synonym of :py:attr:`FACTOR_COST`."""
    MARKET_PRICE = 2
    """Market price, including taxation."""
    NOMINAL = 4
    """Nominal price, as paid in the year incurred."""
    REAL = 8
    """Real price, in a constant price base year."""
    PRESENT_VALUE = 16
    """Discounted real market price."""

    def __init__(self, value, type_, year, discount,
                 deflator, adjustment_factor):
        self.validate_type(type_)
        self.year = year
        self.discount_factor = discount[year]
        self.deflation_factor = 100 / deflator[year]
        self.adjustment_factor = adjustment_factor
        if type_ & self.PRESENT_VALUE:
            value /= self.discount_factor
            type_ = self.MARKET_PRICE | self.REAL
        if type_ & self.REAL:
            value /= self.deflation_factor
            type_ -= (self.REAL - self.NOMINAL)
        if type_ & self.MARKET_PRICE:
            value /= self.adjustment_factor
        self.value = value

    def __eq__(self, other):
        for attr in ("value", "year", "discount_factor",
                     "deflation_factor", "adjustment_factor"):
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __ge__(self, other):
        lt_ = self.__lt__(other)
        if lt_ is NotImplemented:
            return NotImplemented
        return self.__eq__(other) or not lt_

    def __gt__(self, other):
        lt_ = self.__lt__(other)
        if lt_ is NotImplemented:
            return NotImplemented
        return not self.__eq__(other) and not lt_

    def __hash__(self):
        out = 0
        for attr in ("value", "year", "discount_factor",
                     "deflation_factor", "adjustment_factor"):
            out ^= hash(getattr(self, attr))
        return out

    def __le__(self, other):
        lt_ = self.__lt__(other)
        if lt_ is NotImplemented:
            return NotImplemented
        return lt_ or self.__eq__(other)

    def __lt__(self, other):
        for attr in ("year", "discount_factor", "deflation_factor",
                     "adjustment_factor"):
            if getattr(self, attr) != getattr(other, attr):
                return NotImplemented
        return self.value < other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def present_value(self):
        """The Present Value of the :py:class:`Cost` object.

        Returns:
          float: Present Value (discounted real market price, read-only).

        """
        return (self.value * self.adjustment_factor *
                self.deflation_factor * self.discount_factor)

    def as_type(self, type_):
        """Convert the nominal factor cost to the specified ``type_``.

        Arguments:
          type_ (``int``): The type to convert to.

        Returns:
          float: The converted value.

        """
        self.validate_type(type_)
        if type_ & self.PRESENT_VALUE:
            return self.present_value
        value = self.value
        if type_ & self.REAL:
            value *= self.deflation_factor
        if type_ & self.MARKET_PRICE:
            value *= self.adjustment_factor
        return value

    @classmethod
    def validate_type(cls, type_):
        """Validate a cost type argument.

        Costs cannot be both market price and factor/resource cost,
        or both nominal and real. Present values are necessarily
        discounted real market prices.

        Arguments:
          type_ (``int``): The type of the cost.

        Raises:
          ValueError: If the ``type_`` is invalid.

        """
        if (type_ & cls.MARKET_PRICE) and (type_ & cls.FACTOR_COST):
            raise ValueError("Cost cannot be market price and factor cost.")
        if (type_ & cls.NOMINAL) and (type_ & cls.REAL):
            raise ValueError("Cost cannot be real and nominal.")
        if (type_ & cls.NOMINAL) and (type_ & cls.PRESENT_VALUE):
            raise ValueError("Nominal costs cannot be present values.")
        if (type_ & cls.FACTOR_COST) and (type_ & cls.PRESENT_VALUE):
            raise ValueError("Factor costs cannot be present values")
