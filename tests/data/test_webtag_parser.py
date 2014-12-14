import argparse
import json
import os

import pytest

from py_wlc.data import cli, WebTagParser
from py_wlc.data.webtag_parser import parse_args

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

@pytest.fixture()
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

    def test_failure(self):
        with pytest.raises(IOError):
            _ = WebTagParser(COMPFILE)
        with pytest.raises(IOError):
            _ = WebTagParser(os.path.join(DATA, "fail_databook.xls"))
        with pytest.raises(IOError):
            _ = WebTagParser(os.path.join(DATA, "not_databook.xls"))

    def test_context_manager(self):
        with WebTagParser(DATABOOK) as parser:
            assert parser.version == "Nov 2014 release v1.3b"

    def test_setup(self, parser):
        assert parser.version == "Nov 2014 release v1.3b"


class TestParserCli():

    def test_output_file(self, args):
        cli(args)
        assert os.path.exists(TEMPFILE)
        with open(TEMPFILE) as temp, open(COMPFILE) as comp:
            temp_ = json.load(temp)
            comp_ = json.load(comp)
            for dict_ in (temp_, comp_):
                dict_.pop("source")
            assert temp_ == comp_

    def test_failure(self, args):
        args.verbose = True
        args.o = None
        with pytest.raises(ValueError):
            cli(args)

    def test_pipe(self, args):
        args.o = None
        assert cli(args) is None


class TestArgParsing():

    def test_argparse_fail(self):
        with pytest.raises(SystemExit):
            _ = parse_args(['infile', '-v'])

    def test_verbose(self):
        args_ = parse_args(['infile', '-o', 'outfile', '-v'])
        assert args_.verbose
        assert args_.file == "infile"
        assert args_.o == "outfile"

    def test_outfile(self):
        args_ = parse_args(['infile', '-o', 'outfile'])
        assert not args_.verbose
        assert args_.file == "infile"
        assert args_.o == "outfile"

    def test_pipe(self):
        args_ = parse_args(['infile'])
        assert not args_.verbose
        assert args_.file == "infile"
        assert args_.o is None