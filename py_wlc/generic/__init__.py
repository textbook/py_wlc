"""Generic functionality supporting the core modelling."""

from .growth import IndexSeries


class ExtendedDict(dict):
    """Dictionary subclass that provides values beyond defined keys.

    Provides values outside the predefined range, according to the
    following rules:

      * If the key is larger than the largest key in the dictionary,
        the value from the largest key is returned.
      * If the key is smaller than the smallest key in the dictionary,
        the value from the smallest key is returned.
      * If the key is between the smallest and largest keys in the
        dictionary but no value is found, a ``KeyError`` occurs.

    """

    def get(self, key, default=None):
        """Return either the value of the ``key``, or the ``default``.

        Arguments:
          key: The key to return the value of.
          default: The object to return if the key is not found.

        Returns:
          Either the value for the specified ``key``, or ``default``.

        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def copy(self):
        """Create a copy of the extended dictionary.

        Returns:
          ExtendedDict: A new class instance.

        """
        return ExtendedDict(self)

    def __getitem__(self, key):
        try:
            return super(ExtendedDict, self).__getitem__(key)
        except KeyError:
            if self and key > max(self):
                return self[max(self)]
            elif self and key < min(self):
                return self[min(self)]
            else:
                raise

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__,
                                 list(self.items()))
