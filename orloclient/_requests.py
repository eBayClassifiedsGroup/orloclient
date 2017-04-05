from __future__ import print_function
import requests
import logging
from .exceptions import ConnectionError, ServerError

__author__ = 'alforbes'

logger = logging.getLogger(__name__)

"""
Simple wrappers for requests functions, mainly to catch exceptions

orloclient should not raise any exceptions other than those derived from
OrloError.
"""

# Always dealing with JSON, so this is hard-coded
headers = {'Content-Type': 'application/json'}


def get(*args, **kwargs):
    """ Wrapper for exception handling """
    try:
        logger.debug("Get args: {}, kwargs: {}".format(args, kwargs))
        return requests.get(*args, headers=headers, **kwargs)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout):
        raise ConnectionError(
            "Could not connect to Orlo server at {}".format(args[0])
        )
    except requests.exceptions.RequestException as e:
        logger.debug(e.message)
        raise ServerError(
            "Could not read from Orlo server, requests raised {}: {}".format(
                e.__class__.__name__, e.message
            ))


def post(*args, **kwargs):
    """ Wrapper for exception handling """
    try:
        logger.debug("Post args: {}, kwargs: {}".format(args, kwargs))
        return requests.post(*args, headers=headers, **kwargs)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout):
        raise ConnectionError(
            "Could not connect to Orlo server at {}".format(args[0])
        )
    except requests.exceptions.RequestException as e:
        logger.debug(e.message)
        raise ServerError(
            "Could not read from Orlo server at {u}; requests raised {e}: {m}".format(
                u=args[0], e=e.__class__.__name__, m=e.message
            ))
