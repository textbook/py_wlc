import pytest

from py_wlc.economics import GdpDeflator

TOLERANCE = 0.0001

@pytest.fixture(scope="module")
def deflator():
    return GdpDeflator(2010, {2009: 0.03, 2010: 0.03, 2011: 0.03}, True)


class TestDeflator:

    def test_deflator(self):
        deflator = GdpDeflator(2010, {2009: 0.03, 2010: 0.03, 2011: 0.03})
        test = {2008: 0.97087, 2009: 0.97087, 2010: 1,
                2011: 1.03, 2012: 1.0609, 2013: 1.0609}
        for year, val in test.items():
            assert abs(deflator[year] - val) < TOLERANCE

    def test_extended_deflator(self, deflator):
        test = {2007: 0.91514, 2008: 0.94260, 2009: 0.97087,
                2010: 1, 2011: 1.03, 2012: 1.0609, 2013: 1.09273}
        for year, val in test.items():
            assert abs(deflator[year] - val) < TOLERANCE

    def test_empty_rates(self):
        deflator = GdpDeflator(2010, {})
        test = {2009: 1, 2010: 1, 2011: 1}
        for year, val in test.items():
            assert abs(deflator[year] - val) < TOLERANCE

    def test_conversion_factor(self, deflator):
        test = {(2012, 2010): (100 / 106.09),
                (2012,): (100 / 106.09),
                (2010, 2012): (106.09 / 100)}
        for years, val in test.items():
            assert abs(deflator.conversion_factor(*years) - val) < TOLERANCE
