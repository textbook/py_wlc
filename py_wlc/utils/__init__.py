"""General useful functionality."""

from functools import wraps

def memo(func):
    """Memoizing decorator for caching function results.

    Note:
      Currently only implemented for hashable positional arguments.

    Arguments:
      func (``callable``): The function to decorate.

    Returns:
      callable: The decorated function.

    """
    @wraps(func)
    def wrapper(*args):
        """Function returned by decorator."""
        if args not in wrapper.cache:
            wrapper.cache[args] = func(*args)
        return wrapper.cache[args]
    wrapper.cache = {}
    return wrapper
