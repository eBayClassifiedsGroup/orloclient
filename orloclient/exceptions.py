from __future__ import print_function

__author__ = 'alforbes'


class OrloError(Exception):
    """ Root exception """


class ClientError(OrloError):
    """ Client error, e.g. http/400 """


class ServerError(OrloError):
    """ Server error, e.g. http/500 """


class ConnectionError(OrloError):
    """ Connection Error """


# Legacy exceptions for backwards compatibility
OrloClientError = ClientError
OrloServerError = ServerError