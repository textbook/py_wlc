from ..generic import IndexSeries


class Discount(IndexSeries):
    """Discount rates and factors for calculating Present Value.

    The discount rate is assumed to be zero prior to year zero, and
    remain at the rate corresponding to the last year in self.rates
    indefinitely. Similarly, the factor is assumed to be 1.0 prior to
    the base year.

    The initial rate, i.e. the rate corresponding to the smallest
    year in the rates dictionary, is assumed to be the rate from
    the base_year onwards.

    Arguments:
      base_year (int): The base year for discounting, i.e. the year
        in which the factor is 1.0.
      rates (dict of int: float, optional): The discount rates, where
        the key is the start year and the value is the rate to apply.
        Defaults to HM Treasury Green Book rates.
      year_zero (int, optional): Year zero, the year from which the
        applicable rate is incremented. Defaults to base_year.

    Attributes:
      RATES (dict of int: float): The default 'Green Book' discount
        rates (from WebTAG Databook, Dec 2014 edition; correct as of
        2014/12/12).

    """

    RATES = {0: 0.035, 31: 0.03, 76: 0.025, 126: 0.02, 201: 0.015, 301: 0.01}

    def __init__(self, base_year, rates=None, year_zero=None):
        if rates is None:
            rates = self.RATES
        initial_rate = rates[min(rates)]
        super(Discount, self).__init__(base_year, rates,
                                       initial_value=1.0,
                                       year_zero=year_zero,
                                       initial_rate=initial_rate)

    def __getitem__(self, year):
        try:
            return super(Discount, self).__getitem__(year)
        except KeyError:
            return 1.0

    def _rate(self, year):
        if year < (self.base_year - self.year_zero):
            return 0.0
        return super(Discount, self)._rate(year)

    def _extend_values(self, year):
        for year_ in range(max(self._values), year):
            self._values[year_+1] = (self._values[year_] /
                                     (1.0 + self._rate(year_+1)))
