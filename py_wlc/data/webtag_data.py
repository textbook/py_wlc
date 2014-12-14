"""Exposes the parsed WebTAG data as :py:mod:`py_wlc` objects."""
import datetime
import json
import logging
from os import path, walk

from ..economics import Discount


logger = logging.getLogger(__name__)


class WebTagData(object):
    """Holds the data extracted from WebTAG."""

    def __init__(self, base_year, released, version, source, **data):
        self.base_year = base_year
        released = datetime.datetime.strptime(released, "%Y-%m-%d")
        self.released = released.date()
        if (datetime.datetime.now() - released).days > 365:
            logger.warning("WebTAG data is more than one year old")
        self.version = version
        self.source = source
        self.discount = self._parse_discount(data.get("discount_rate"))

    def _parse_discount(self, data):
        """Parse the discount data from WebTAG into a ``Discount``.

        Notes:
          Assumes that all years will be in dash-separated or space-
          separated format, with the first part being the start year.

        Arguments:
          data (dict): The dictionary of discount rate data (or
            ``None`` if not present - this will produce a
            :py:class:`~.Discount` with the default rates).

        Returns:
          :py:class:`~.Discount`: The new Discount object.

        """
        if data is not None:
            rates = {}
            for key, val in data.items():
                if "-" in key:
                    key = int(key.split("-")[0])
                else:
                    key = key.split(" ")[0]
                    if key.isdigit():
                        key = int(key)
                    else:
                        continue
                rates[key] = val
            return Discount(self.base_year, rates)
        return Discount(self.base_year)

    @classmethod
    def from_latest_json(cls, dir_):
        """Extract data from the most recent JSON in the directory.

        Arguments:
          dir_ (str): The directory to start from.

        Returns:
          :py:class:`~.WebTagData`: A new class instance.

        """
        latest_data = latest_date = None
        for curdir, _, files in walk(dir_):
            for file in files:
                if file.endswith(".json"):
                    with open(path.join(curdir, file)) as file_:
                        data = json.load(file_)
                    date = data.get("released", "")
                    if latest_date is None or date > latest_date:
                        latest_data = data
                        latest_date = date
        if latest_data is not None:
            return cls(**latest_data)

    @classmethod
    def from_json(cls, file):
        """Extract data from the specified JSON.

        Arguments:
          file (str): The file to import from.

        Returns:
          :py:class:`~.WebTagData`: A new class instance.

        """
        with open(file) as file_:
            data = json.load(file_)
        return cls(**data)

