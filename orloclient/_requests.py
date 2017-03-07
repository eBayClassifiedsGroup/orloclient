from __future__ import print_function
import requests
from .exceptions import ConnectionError

__author__ = 'alforbes'


"""
Simple wrappers for requests functions
"""

# Always dealing with JSON, so this is hard-coded
headers = {'Content-Type': 'application/json'}


def get(*args, **kwargs):
    """ Wrapper for exception handling """
    try:
        return requests.get(*args, headers=headers, **kwargs)
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to Orlo server")


def post(*args, **kwargs):
    """ Wrapper for exception handling """
    try:
        return requests.post(*args, headers=headers, **kwargs)
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to Orlo server")
