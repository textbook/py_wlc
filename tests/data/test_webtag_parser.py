import json
import os

import pytest

from py_wlc.data import cli, WebTagParser

DATA = os.path.join(os.getcwd(), "tests", "data")
DATABOOK = os.path.join(DATA, "test_databook.xls")
TEMPFILE = os.path.join(DATA, "temp.json")
COMPFILE = os.path.join(DATA, "test_databook.json")

@pytest.fixture(scope='module')
def parser(request):
    parser = WebTagParser(DATABOOK)
    def clean_up():
        parser.close()
    request.addfinalizer(clean_up)
    return parser

@pytest.fixture(scope='module')
def args(request):
    # Create generic arguments
    class Generic():
        pass
    args = Generic()
    args.verbose = False
    args.file = DATABOOK
    args.o = TEMPFILE
    # Handle file clean-up
    def clean_up():
        if os.path.exists(TEMPFILE):
            os.remove(TEMPFILE)
    request.addfinalizer(clean_up)
    return args


class TestWebTagParser():

    def test_cli(self, args):
        cli(args)
        assert os.path.exists(TEMPFILE)
        with open(TEMPFILE) as temp, open(COMPFILE) as comp:
            temp_ = json.load(temp)
            comp_ = json.load(comp)
            for dict_ in (temp_, comp_):
                dict_.pop("source")
            assert temp_ == comp_

    def test_context_manager(self):
        with WebTagParser(DATABOOK) as parser:
            assert parser.version == "Nov 2014 release v1.3b"

    def test_setup(self, parser):
        assert parser.version == "Nov 2014 release v1.3b"
