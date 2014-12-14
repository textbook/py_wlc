"""General useful functionality."""

from functools import wraps

def memo(func):
    """Memoizing decorator for caching function results.

    Note:
      Currently only implemented for positional arguments.

    """
    @wraps(func)
    def wrapper(*args):
        if args not in wrapper.cache:
            wrapper.cache[args] = func(*args)
        return wrapper.cache[args]
    wrapper.cache = {}
    return wrapper
