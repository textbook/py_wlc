"""Exposes the parsed WebTAG data as :py:mod:`py_wlc` objects."""
import datetime
import json
import logging
from os import path, walk

from ..economics import Discount, GdpDeflator


logger = logging.getLogger(__name__)


class WebTagData:
    """Holds the data extracted from WebTAG."""

    def __init__(self, base_year, released, version, source, **data):
        self.base_year = base_year
        released = datetime.datetime.strptime(released, "%Y-%m-%d")
        self.released = released.date()
        if (datetime.datetime.now() - released).days > 365:
            logger.warning("WebTAG data is more than one year old")
        self.version = version
        self.source = source
        self.discount = self._parse_discount(data.get("discount_rate"),
                                             self.base_year)
        self.deflator = self._parse_deflator(data.get("gdp_growth"),
                                             self.base_year)

    @staticmethod
    def _parse_deflator(data, base_year):
        """Parse GDP data from WebTAG into :py:class:`~.GdpDeflator`.

        Arguments:
          data (``dict`` or ``None``): The dictionary of GDP data (or
            ``None`` - this will produce a :py:class:`~.GdpDeflator`
            with zero rates).
          base_year (``int``): The base year for the new
            :py:class:`~.GdpDeflator` object.

        Returns:
          :py:class:`~.GdpDeflator`: The new GdpDeflator object.

        """
        if data is not None:
            rates = {}
            for key, val in data.items():
                if key.isdigit():
                    rates[int(key)] = float(val)
            return GdpDeflator(base_year, rates, True)
        return GdpDeflator(base_year, {base_year: 0.0}, True)

    @staticmethod
    def _parse_discount(data, base_year):
        """Parse discount data from WebTAG into :py:class:`~.Discount`.

        Assumes that all years will be in dash-separated or space-
        separated format, with the first part being the start year.

        Arguments:
          data (``dict`` or ``None``): The dictionary of discount rate
            data (or ``None`` - this will produce a
            :py:class:`~.Discount` with the default rates).
          base_year (``int``): The base year for the new
            :py:class:`~.Discount` object.

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
                        continue  # pragma: no cover
                rates[key] = val
            return Discount(base_year, rates)
        return Discount(base_year)

    @classmethod
    def from_latest_json(cls, dir_):
        """Extract data from the most recent JSON in the directory.

        Arguments:
          dir_ (``str``): The directory to start searching from.

        Returns:
          :py:class:`~.WebTagData`: A new class instance.

        """
        latest_data = latest_date = None
        for curr_dir, _, files in walk(dir_):
            for file in files:
                with open(path.join(curr_dir, file)) as file_:
                    try:
                        data = json.load(file_)
                    except ValueError:
                        pass
                    else:
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
          file (``str``): The file to import from.

        Returns:
          :py:class:`~.WebTagData`: A new class instance.

        """
        with open(file) as file_:
            data = json.load(file_)
        return cls(**data)
