import pytest

from py_wlc.economics import Discount

TOLERANCE = 0.0001

@pytest.fixture(scope='module')
def green_book():
    return Discount(2010)


class TestStandardDiscount:
    """Test a simple Discount against Green Book rates."""

    def test_setup(self, green_book):
        assert green_book.base_year == green_book.year_zero
        assert abs(green_book._final_rate - 0.01) < TOLERANCE

    def test_rates(self, green_book):
        assert abs(green_book.rate(-10)) < TOLERANCE
        assert abs(green_book.rate(400) - 0.01) < TOLERANCE

    def test_factors(self, green_book):
        factors = {2005: 1.0000, 2010: 1.0000, 2020: 0.7089,
                   2030: 0.5026, 2050: 0.2651, 2135: 0.0274}
        for year, fact in factors.items():
            assert abs(green_book[year] - fact) < TOLERANCE

    def test_parent_magic_methods(self, green_book):
        book_two = Discount(2010)
        assert green_book == book_two
        hash_ = hash(green_book)
        assert hash_ == hash(book_two)
        assert hash(green_book) == hash_
        assert len(book_two) == 1
        for year in book_two:
            assert year == 0


class TestComplexDiscount:
    """Test complex discounting against DfT RIOC v1.4."""

    def test_factor(self, green_book):
        complex_discount = green_book.rebase(2014)
        assert abs(complex_discount[2160] - 0.0158) < TOLERANCE