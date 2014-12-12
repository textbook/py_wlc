import pytest

from py_wlc import Discount

TOLERANCE = 0.0001

@pytest.fixture(scope='module')
def green_book():
    return Discount(2010)

@pytest.fixture(scope='module')
def complex_discount():
    return Discount(2010, year_zero=2014)


class TestStandardDiscount:
    """Test a simple Discount against Green Book rates."""

    def test_setup(self, green_book):
        assert green_book.base_year == green_book.year_zero
        assert abs(green_book._final_rate - 0.01) < TOLERANCE

    def test_rates(self, green_book):
        assert abs(green_book._rate(-10)) < TOLERANCE
        assert abs(green_book._rate(400) - 0.01) < TOLERANCE

    def test_factors(self, green_book):
        assert abs(green_book[2005] - 1.0) < TOLERANCE
        assert abs(green_book[2020] - 0.7089) < TOLERANCE
        assert abs(green_book[2030] - 0.5026) < TOLERANCE
        assert abs(green_book[2050] - 0.2651) < TOLERANCE
        assert abs(green_book[2135] - 0.0274) < TOLERANCE


class TestComplexDiscount:
    """Test complex discounting against DfT RIOC v1.4."""

    def test_factor(self, complex_discount):
        assert abs(complex_discount[2160] - 0.0158) < TOLERANCE