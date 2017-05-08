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


class BaseClient(object):
    def __init__(self, timeout=10, verify_ssl=True):
        self.request_args = {
            'timeout': timeout,
            'verify': verify_ssl
        }
        self.get_headers = {'Content-Type': 'application/json'}

    def _get(self, *args, **kwargs):
        """
        Wraps a GET request with standard parameters
        """
        try:
            req_kw_args = self.request_args.copy()
            req_kw_args.update(kwargs)
            logger.debug("Get args: {}, kwargs: {}".format(args, req_kw_args))
            return requests.get(
                *args,
                headers=self.get_headers,
                **req_kw_args
            )
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout) as e:
            logger.debug('Requests exception: {}\n{}'.format(
                e.__class__.__name__, e.message
            ))
            raise ConnectionError(
                "{} while connecting to Orlo server at {}.".format(
                    e.__class__.__name__, args[0])
            )
        except requests.exceptions.RequestException as e:
            logger.debug(e.message)
            raise ServerError(
                "Could not read from Orlo server, requests raised {}: {}".format(
                    e.__class__.__name__, e.message
                ))


    def _post(self, *args, **kwargs):
        """
        Wraps a POST request with standard parameters
        """
        try:
            req_kw_args = self.request_args.copy()
            req_kw_args.update(kwargs)
            logger.debug("Post args: {}, kwargs: {}".format(args, req_kw_args))
            return requests.post(
                *args,
                **req_kw_args
            )
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
