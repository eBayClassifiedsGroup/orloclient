from __future__ import print_function
from .exceptions import OrloClientError
import json
import arrow
import uuid

__author__ = 'alforbes'


def cast_type(item, value):
    """
    Cast the item as the correct type

    Some non-base objects (times and uuids) need to be cast manually.
    Rest are already the correct type courtesy of being imported with json.loads.

    :param item:
    :param value:
    """
    if item.endswith('_id') or item == 'id':
        return uuid.UUID(value)
    if 'time' in item:
        return arrow.get(value)

    # If no matches, return as given
    return value


class Release(object):
    def __init__(self, client, release_id):
        """
        A base class to handle fetching attributes from the Orlo server

        :param client: OrloClient instance pointing to the server
        """
        self.client = client
        # Don't access this directly before calling fetch(), or you get None
        # Recommend not using it at all, use "data" instead
        self._data = None

        self.release_id = release_id

    def __getattr__(self, item):
        """
        Fetch the attribute from Orlo

        We override getattr for this rather than getattribute, as getattribute
        is always called, whereas getattr is only called when the attribute
        doesn't exist

        :param item:
        :return:
        """
        if not object.__getattribute__(self, '_data'):
            self.fetch()

        # For returning the raw data
        if item == 'data':
            return self._data

        try:
            # The data returned by Orlo is a JSON structure, containing a list
            # of releases, even though there can only be one
            if len(self._data['releases']) > 1:
                raise OrloClientError("Expected one release in dictionary")
            value = self._data['releases'][0][item]
        except KeyError:
            raise OrloClientError("This object does not have attribute '{}'\n{}".format(
                item, json.dumps(self._data, indent=2)
            ))

        return cast_type(item, value)

    def fetch(self):
        """
        Fetch the data for a release
        """
        release = self.client.get_releases(release_id=self.release_id)
        self._data = json.loads(release)

    def deploy(self):
        raise NotImplementedError("Coming soon")


class Package(object):
    def __init__(self, release, package_id):
        """
        An Orlo Package

        At the moment, Packages are dependant on release, as there is no /packages endpoint

        Thus, this just fetches the values from its parent release
        :param Release release:
        :param UUID package_id:
        :return:
        """
        # Don't use these
        self._release = release
        self._package_id = package_id
        self._data = None

    def __getattr__(self, item):
        """
        The release holds all the information about the packages,
        so fetch attributes from parent

        :param item:
        :return:
        """
        if not self._data:
            release = object.__getattribute__(self, '_release')
            self._data = [p for p in release.packages if p['id'] == self._package_id]

        try:
            return cast_type(item, self._data[0][item])
        except KeyError:
            raise OrloClientError("This object does not have attribute '{}'\n{}".format(
                item, json.dumps(self._data, indent=2)
            ))

