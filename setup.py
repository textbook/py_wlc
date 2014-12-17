import io
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

import py_wlc

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(author='Jonathan Sharpe',
      author_email='j.r.sharpe@gmail.com',
      classifiers=['Programming Language :: Python',
                   'Development Status :: 2 - Pre-Alpha',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering'],
      cmdclass={'test': PyTest},
      description='Functionality for whole-life costing in Python',
      extras_require={'testing': ['pytest']},
      include_package_data=True,
      install_requires=['xlrd>=0.9.3'],
      license='License :: OSI Approved :: MIT License',
      long_description=long_description,
      name='py_wlc',
      packages=['py_wlc'],
      platforms='any',
      scripts=['py_wlc/data/webtag_parser.py'],
      test_suite='py_wlc.test.test_py_wlc',
      tests_require=['pytest'],
      url='http://github.com/textbook/py_wlc/',
      version=py_wlc.__version__)
