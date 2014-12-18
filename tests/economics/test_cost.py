import pytest

from py_wlc.economics import Cost, Discount, GdpDeflator

TOLERANCE = 0.0001


@pytest.fixture(scope="module")
def discount():
    return Discount(2010)

@pytest.fixture(scope="module")
def deflator():
    return GdpDeflator(2010, {2010: 0.03}, True)


class TestClassMethods:

    def test_validate_type_fail(self):
        for fail in (Cost.MARKET_PRICE | Cost.FACTOR_COST,
                     Cost.MARKET_PRICE | Cost.RESOURCE_COST,
                     Cost.REAL | Cost.NOMINAL,
                     Cost.NOMINAL | Cost.PRESENT_VALUE,
                     Cost.FACTOR_COST | Cost.PRESENT_VALUE):
            with pytest.raises(ValueError):
                Cost.validate_type(fail)

    def test_validate_type_pass(self):
        for pass_ in (Cost.MARKET_PRICE | Cost.REAL,
                      Cost.FACTOR_COST | Cost.REAL,
                      Cost.MARKET_PRICE | Cost.NOMINAL,
                      Cost.FACTOR_COST | Cost.NOMINAL):
            assert Cost.validate_type(pass_) is None
            if not ((Cost.NOMINAL & pass_) or (Cost.FACTOR_COST & pass_)):
                assert Cost.validate_type(pass_ | Cost.PRESENT_VALUE) is None


class TestInitialisation:

    def test_simple_init(self, discount, deflator):
        cost = Cost(100, Cost.NOMINAL, 2010, discount, deflator, 1)
        assert abs(cost.present_value - 100) < TOLERANCE

    def test_init_fail(self, discount, deflator):
        with pytest.raises(ValueError):
            _ = Cost(100, Cost.NOMINAL | Cost.REAL,
                     2010, discount, deflator, 1)

    def test_deflation(self, discount, deflator):
        cost = Cost(100, Cost.NOMINAL, 2011, discount, deflator, 1)
        assert abs(cost.as_type(Cost.REAL) - (100 / 1.03)) < TOLERANCE

    def test_adjustment(self, discount, deflator):
        cost = Cost(100, Cost.NOMINAL, 2010, discount, deflator, 1.19)
        assert abs(cost.as_type(Cost.MARKET_PRICE) - 119) < TOLERANCE

    def test_real_market_price(self, discount, deflator):
        cost = Cost(100, Cost.NOMINAL, 2011, discount, deflator, 1.19)
        assert abs(cost.as_type(Cost.REAL | Cost.MARKET_PRICE) -
                   (119 / 1.03)) < TOLERANCE

    def test_present_value(self, discount, deflator):
        cost = Cost(100, Cost.PRESENT_VALUE, 2011, discount, deflator, 1.19)
        assert abs(cost.as_type(Cost.PRESENT_VALUE) -
                   cost.present_value) < TOLERANCE
        assert abs(cost.present_value - 100) < TOLERANCE


class TestMethods:

    def test_equality(self, discount, deflator):
        cost1 = Cost(100, Cost.NOMINAL, 2011, discount, deflator, 1.19)
        cost2 = Cost(119, Cost.MARKET_PRICE, 2011, discount, deflator, 1.19)
        assert cost1 == cost2
        assert hash(cost1) == hash(cost2)
        cost3 = Cost(100, Cost.REAL, 2011, discount, deflator, 1.19)
        assert cost1 != cost3

    def test_comparison(self, discount, deflator):
        cost1 = Cost(100, Cost.NOMINAL, 2011, discount, deflator, 1.19)
        cost2 = Cost(90, Cost.NOMINAL, 2011, discount, deflator, 1.19)
        assert cost1 > cost2
        assert cost2 < cost1
        assert cost1 >= cost2
        assert cost2 <= cost1

    def test_comp_fail(self, discount, deflator):
        cost1 = Cost(100, Cost.NOMINAL, 2011, discount, deflator, 1.19)
        cost2 = Cost(100, Cost.NOMINAL, 2011, discount, deflator, 1)
        with pytest.raises(TypeError):
            cost2 > cost1
        with pytest.raises(TypeError):
            cost2 < cost1
        with pytest.raises(TypeError):
            cost2 <= cost1
        with pytest.raises(TypeError):
            cost2 >= cost1
        assert cost1 != cost2