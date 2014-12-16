import pytest

from py_wlc.generic import ExtendedDict

@pytest.fixture(scope="module")
def ext_dict():
    return ExtendedDict({-1: 1, 1: 2})


class TestExtendedDict:

    def test_getitem(self, ext_dict):
        assert ext_dict[-2] == 1
        assert ext_dict[-1] == 1
        assert ext_dict[1] == 2
        assert ext_dict[2] == 2
        with pytest.raises(KeyError):
            _ = ext_dict[0]

    def test_get(self, ext_dict):
        assert ext_dict.get(0) is None
        assert ext_dict.get(0, 0) == 0
