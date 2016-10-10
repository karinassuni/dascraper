import logging
import requests
import sys
from functools import wraps


def attempt(method, url, **kwargs):
    try:
        r = requests.request(method, url, **kwargs)
    except requests.exceptions.RequestException:
        logging.exception("Something went wrong with the request! Exiting...")
        sys.exit(1)
    else:
        return r


def get(func):
    @wraps(func)
    def decorator(url, params=None, **kwargs):
        return func(attempt("GET", url, params=params, **kwargs))
    return decorator
