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

    :param item: The parameter/variable name
    :param value: The value to cast
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

        :param string release_id: Release ID
        :param OrloClient() client: OrloClient instance pointing to the server
        """
        self.client = client
        # Don't access this directly before calling fetch(), or you get None
        # Recommend not using it at all, use "data" instead
        self._data = None

        self.id = self.release_id = release_id
        self.uuid = uuid.UUID(release_id)

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

        if item == 'packages':
            return self.list_packages()

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

    def list_packages(self):
        """
        Return a list of Package objects

        :return list:
        """
        l = []
        data = self.data
        for p in self.data['releases'][0]['packages']:
            # Create Package
            pkg = Package(self.id, p['id'], p['name'], p['version'])

            # Set all attributes from the data
            for item, value in p.items():
                setattr(pkg, item, cast_type(item, value))
            l.append(pkg)
        return l

    def fetch(self):
        """
        Fetch the data for a release
        """
        self._data = self.client.get_release_json(self.release_id)

    def deploy(self):
        """
        Issue the deploy command
        """
        status = self.client.deploy_release(self.release_id)
        return status

    def add_package(self, name, version):
        """
        Create a package and add it to this release

        :param name:
        :param version:
        """
        pkg = self.client.create_package(self, name, version)
        return pkg


class Package(object):
    def __init__(self, release_id, package_id, package_name, version):
        """
        An Orlo Package

        Only these attributes are required, the rest may or may not be set.
        """
        self.id = package_id
        self.name = package_name
        self.release_id = release_id
        self.version = version


