"""Representation of cost objects in various bases and forms."""
from functools import total_ordering


@total_ordering
class Cost:
    """Represents costs and holds data for type conversions.

    The ``type_`` of a cost is necessary for conversion between the
    different types; costs can be provide in real or nominal terms and
    as a factor (or "resource") cost or a market price. Additionally, a
    cost can be a Present Value (discounted real factor cost or market
    price).

    It is essential for an accurate calculation that the appropriate
    cost type is used for conversion to consistent output values.

    Note:
      The default assumptions for ``type_`` are :py:attr:`NOMINAL` and
      :py:attr:`FACTOR_COST`. For example::

          Cost(100, Cost.REAL, ...)

      is equivalent to::

          Cost(100, Cost.REAL | Cost.FACTOR_COST, ...)

      The exception is :py:attr:`PRESENT_VALUE`, which is always a real
      cost.

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
        Value (from real factor costs or market prices).
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
    """Discounted real costs."""

    def __init__(self, value, type_, year, discount,
                 deflator, adjustment_factor):
        self.validate_type(type_)
        self.year = year
        self.discount_factor = discount[year]
        self.deflation_factor = 1 / deflator[year]
        self.adjustment_factor = adjustment_factor
        if type_ & self.PRESENT_VALUE:
            value /= self.discount_factor
            type_ |= self.REAL
        if type_ & self.REAL:
            value /= self.deflation_factor
        if type_ & self.MARKET_PRICE:
            value /= self.adjustment_factor
        self.value = value
        self.hash_ = None

    def __eq__(self, other):
        for attr in ("value", "year", "discount_factor",
                     "deflation_factor", "adjustment_factor"):
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __hash__(self):
        if self.hash_ is None:
            out = 0
            for attr in ("value", "year", "discount_factor",
                         "deflation_factor", "adjustment_factor"):
                out ^= hash(getattr(self, attr))
            self.hash_ = out
        return self.hash_

    def __lt__(self, other):
        for attr in ("year", "discount_factor", "deflation_factor",
                     "adjustment_factor"):
            if getattr(self, attr) != getattr(other, attr):
                return NotImplemented
        return self.value < other.value

    def as_type(self, type_):
        """Convert the nominal factor cost to the specified ``type_``.

        Arguments:
          type_ (``int``): The type to convert to.

        Returns:
          float: The converted value.

        """
        self.validate_type(type_)
        value = self.value
        if type_ & self.PRESENT_VALUE:
            value *= self.discount_factor
            type_ |= self.REAL
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
        discounted real factor costs or market prices.

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
