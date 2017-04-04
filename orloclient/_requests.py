from __future__ import print_function
import requests
import logging
from .exceptions import ConnectionError

__author__ = 'alforbes'

logger = logging.getLogger(__name__)

"""
Simple wrappers for requests functions
"""

# Always dealing with JSON, so this is hard-coded
headers = {'Content-Type': 'application/json'}


def get(*args, **kwargs):
    """ Wrapper for exception handling """
    try:
        logger.debug("Get args: {}, kwargs: {}".format(args, kwargs))
        return requests.get(*args, headers=headers, **kwargs)
    except requests.exceptions.ConnectionError as e:
        logger.debug(e.message)
        raise ConnectionError("Could not connect to Orlo server")


def post(*args, **kwargs):
    """ Wrapper for exception handling """
    try:
        logger.debug("Post args: {}, kwargs: {}".format(args, kwargs))
        return requests.post(*args, headers=headers, **kwargs)
    except requests.exceptions.ConnectionError as e:
        logger.debug(e.message)
        raise ConnectionError("Could not connect to Orlo server")
