import os

import pytest

from py_wlc import WebTagData

DATA = os.path.join(os.getcwd(), 'tests', 'data')

@pytest.fixture(scope='module')
def databook():
    return WebTagData.from_json(os.path.join(DATA, "test_databook.json"))

@pytest.fixture(scope='module')
def latest_databook():
    return WebTagData.latest_json(DATA)


class TestWebTagData():

    def test_databook(self, databook):
        assert databook.version == "Nov 2014 release v1.3b"

    def test_latest_databook(self, latest_databook):
        assert latest_databook.version == "Nov 2014 release v1.3b"