from py_wlc.economics.residual_value import ResidualValueCalculator

TOLERANCE = 0.0001


class TestResidualValue:

    def test_linear(self):
        calc = ResidualValueCalculator("linear")
        for end, val in [(0, 17000), (1, 14000), (2, 11000),
                         (3, 8000), (4, 5000), (5, 2000)]:
            result = calc.calculate(17000, 5, 0, end, 2000)
            assert abs(result - val) < TOLERANCE

    def test_sum_of_years(self):
        calc = ResidualValueCalculator("sum of years' digits")
        for end, val in [(0, 1000), (1, 700), (2, 460),
                         (3, 280), (4, 160), (5, 100)]:
            result = calc.calculate(1000, 5, 0, end, 100)
            assert abs(result - val) < TOLERANCE

    def test_double_declining(self):
        calc = ResidualValueCalculator("double-declining")
        for end, val in [(0, 1000), (1, 600), (2, 360),
                         (3, 216), (4, 129.60), (5, 100)]:
            result = calc.calculate(1000, 5, 0, end, 100)
            assert abs(result - val) < TOLERANCE