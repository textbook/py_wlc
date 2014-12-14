import os

import pytest

from py_wlc import Discount, WebTagData

DATA = os.path.join(os.getcwd(), 'tests', 'data')

@pytest.fixture(scope='module')
def databook():
    return WebTagData.from_json(os.path.join(DATA, "test_databook.json"))

@pytest.fixture(scope='module')
def latest_databook():
    return WebTagData.from_latest_json(DATA)


class TestWebTagData():

    def test_databook(self, databook):
        assert databook.version == "Nov 2014 release v1.3b"

    def test_latest_databook(self, latest_databook):
        assert latest_databook.version == "Nov 2014 release v1.3b"

    def test_discount_parsing(self):
        data = {"0 to 30": 0.035, "text": None, "31-75": 0.03}
        disc = WebTagData._parse_discount(data, 2010)
        assert disc == Discount(2010, {0: 0.035, 31: 0.03})
        assert WebTagData._parse_discount(None, 2010) == Discount(2010)