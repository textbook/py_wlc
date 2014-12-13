#! /usr/bin/env python
"""WebTAG Parser - functionality for extracting from the Data Book.

This class parses the databook to a more convenient JSON format for
use by :py:class:`~.WebTagData`.

"""
import argparse
import datetime
import json
from os import path
from sys import stdout

import xlrd


class WebTagParser(object):
    """Class to handle access to a WebTAG Databook Excel file.

    The class is designed to operate as a context manager if needed.

    Notes:
      Where possible, the workbook is opened in ``on_demand`` mode, to
      avoid loading all worksheets at once. :py:meth:`extract_data`
      will load and unload the appropriate worksheet as required.

    Arguments:
      filename (``str``): The WebTAG Databook file to open.

    Attributes:
      book (``xlrd.Workbook``): The Excel workbook.
      date (``datetime.datetime``): The release date of the databook.
      filename (``str``): The name of the file to open.
      version (``str``): The version of the databook.

    """

    BASE = ("User Parameters", 0, 11, "Price year")
    CHECK = ("Cover", 2, 0, "WebTAG Databook")
    DATE = ("Audit", 0, 2)
    LOCATIONS = {"discount_rate": ("A1.1.1", 24, 1, 3),
                 "rail_diesel_price": ("A1.3.7", 27, 1, 5),
                 "rail_electricity_price": ("A1.3.7", 27, 1, 7),
                 "rail_fuel_duty": ("A1.3.7", 27, 1, 10),
                 "gdp_growth": ("Annual Parameters", 30, 1, 5)}

    def __init__(self, filename):
        self.filename = filename
        sht, row, col, val = self.CHECK
        err_msg = "Not a WebTAG Databook."
        try:
            self.book = xlrd.open_workbook(filename, on_demand=True)
            sheet = self.book.sheet_by_name(sht)
        except xlrd.XLRDError:
            raise IOError(err_msg)
        try:
            compare = sheet.cell(row, col).value
        except IndexError:
            raise IOError(err_msg)
        if compare != val:
            raise IOError(err_msg)
        self.version = sheet.cell(3, 0).value
        self.date = self._extract_date(*self.DATE)
        self.base_year = self._extract_base(*self.BASE)

    def _extract_base(self, sheet_name, label_col, base_col, label):
        """Extract the base year from the appropriate worksheet.

        Arguments:
          sheet_name (``str``): The worksheet from which to extract
            the base year.
          label_col (``int``): The column in which to find the label.
          base_col (``int``): The column from which to extract the base
            year.
          label (``str``): The label to find in ``label_col``.

        Returns:
          ``int``: The base year for the data in the workbook.

        """
        sheet = self.book.sheet_by_name(sheet_name)
        base_row = sheet.col_values(label_col).index(label)
        base = sheet.col_values(base_col)[base_row]
        self.book.unload_sheet(sheet_name)
        return int(base)

    def _extract_date(self, sheet_name, version_col, date_col):
        """Extract the version's date from the appropriate worksheet.

        Notes:
          Expects that the date will be in the date_col on the same row
          as the version appears in version_col.

        Arguments:
          date_col (``int``): The column from which to extract the
            date.
          sheet_name (``str``): The worksheet from which to extract the
            date.
          version_col (``int``): The column in which to find the
            version.

        Returns:
          ``datetime.date``: The release date of the workbook.

        """
        sheet = self.book.sheet_by_name(sheet_name)
        date_row = sheet.col_values(version_col).index(self.version)
        date = xlrd.xldate_as_tuple(sheet.col_values(date_col)[date_row],
                                    self.book.datemode)
        self.book.unload_sheet(sheet_name)
        return datetime.date(*date[:3])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.book.release_resources()

    def close(self):
        """Close the file release the :py:attr:`book` resources."""
        self.__exit__()

    def extract_all(self, verbose=False):
        """Extract all data from ``LOCATIONS`` and useful metadata."""
        data = {}
        for name in self.LOCATIONS:
            if verbose:
                print("Extracting {}".format(name))
            data[name] = self.extract_named_data(name)
        if verbose:
            print("Extracting metadata")
        data["source"] = path.split(self.filename)[-1]
        data["released"] = str(self.date)
        data["version"] = self.version
        data["base_year"] = self.base_year
        return data

    def extract_data(self, sheet_name, start_row, label_col, value_col):
        """Extract data from the specified worksheet."""
        sheet = self.book.sheet_by_name(sheet_name)
        labels = sheet.col_values(label_col)[start_row:]
        values = sheet.col_values(value_col)[start_row:]
        try:
            data = {int(k): v for k, v in zip(labels, values) if k}
        except ValueError:
            data = {k: v for k, v in zip(labels, values) if k}
        self.book.unload_sheet(sheet_name)
        data["title"] = sheet.cell(2, 0).value
        data["table"] = sheet.cell(3, 0).value
        return data

    def extract_named_data(self, name):
        """Extract a named data series from ``LOCATIONS``."""
        return self.extract_data(*self.LOCATIONS[name])


def parse_args(): # pragma: no cover
    """Parse the arguments for :py:func:`cli`.

    Raises:
      ArgumentError: If both ``-v`` and ``-o`` are supplied.

    """
    description = "Convert a WebTAG Databook to JSON"
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.add_argument("file",
                            help="file to parse")
    group1 = arg_parser.add_argument_group("Output to file",
                                           "Choose file rather than pipe.")
    group1.add_argument("-o",
                        help="file to output to")
    verbose = group1.add_argument("-v", "--verbose",
                                  action="store_true",
                                  help="increase output verbosity")
    args_ = arg_parser.parse_args()
    if args_.o is None and args_.verbose:
        msg = "Verbose mode not supported unless output file supplied."
        raise argparse.ArgumentError(verbose, msg)
    return args_


def cli(args):
    """Provide a CLI for the :py:class:`~.WebTagParser`.

    Notes:
      Will either output to a specified file (with optional verbose
      reporting) or dump the JSON data to ``stdout``.

    Arguments:
      args (``argparse.Namespace``): The parsed command line arguments.

    Raises:
      ValueError: If both ``-v`` and ``-o`` are supplied.

    """
    if args.o is None and args.verbose:
        raise ValueError("Verbose mode not supported unless output file set.")
    if args.verbose:
        print("Reading from input file {}".format(args.file))
    with WebTagParser(args.file) as parser:
        data = parser.extract_all(args.verbose)
        if args.verbose:
            print("Data extracted from input file")
    if args.o is not None:
        with open(args.o, "w") as outfile:
            if args.verbose:
                print("Writing to output file {}".format(args.o))
            json.dump(data, outfile, indent=4)
    else:
        stdout.write(json.dumps(data, indent=4))



if __name__ == "__main__":
    cli(parse_args())