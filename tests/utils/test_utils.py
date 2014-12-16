from operator import mul as func

import pytest

from py_wlc.utils import memo

@pytest.fixture(scope='module')
def decorated_func():
    return memo(func)


class TestMemo:

    def test_memo(self, decorated_func):
        decorated_func.cache = {}
        assert decorated_func(2, 2) == func(2, 2)
        assert decorated_func(2, 2) == func(2, 2)
        assert decorated_func.cache == {(2, 2): 4}

    def test_memo_fail(self, decorated_func):
        with pytest.raises(TypeError):
            _ = decorated_func({}, [])
