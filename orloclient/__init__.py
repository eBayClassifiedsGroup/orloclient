from __future__ import print_function
from orloclient.config import config
from orloclient.exceptions import OrloClientError, OrloServerError
import logging
import json
import requests
import uuid

RELEASE_FILTERS = (
    "package_name",
    "user",
    "platform",
    "stime_before",
    "stime_after",
    "ftime_before",
    "ftime_after",
    "duration_less",
    "duration_greater",
    "team",
)

PACKAGE_FILTERS = (
    "name",
    "version",
)


class Orlo(object):
    """
    Reference object to our Orlo server
    """

    headers = {
        'Content-Type': 'application/json',
    }

    def __init__(self, uri):
        self.logger = logging.getLogger(__name__)
        self.uri = uri

    def ping(self):
        response = requests.get(self.uri + '/ping')
        if response.status_code == 200:
            return True
        else:
            return False

    def get_releases(self, release_id=False, **kwargs):
        """
        Fetch releases from the orlo API, optionally filtering

        http://orlo.readthedocs.org/en/latest/rest.html#get--releases
        """
        self.logger.debug("Entering get_releases")

        if release_id:
            "{url}/{id}".format(url=self.uri, id=release_id)
        else:
            url = self.uri

        filters = []

        for key in kwargs:
            if key not in RELEASE_FILTERS:
                raise OrloClientError("Invalid filter '{}' specified".format(
                    key, kwargs[key]
                ))
            else:
                f = "{}={}".format(key, kwargs[key])
                self.logger.debug("Append filter {}".format(f))
                filters.append(f)

        response = requests.get(url, headers=self.headers)
        return response.json()

    def create_release(self, user, team, platforms,
                       references=None,
                       note=None,
                       ):
        """
        Create a release using the REST API
        """

        data = {
            'team': team,
            'user': user,
        }

        if platforms:
            data['platforms'] = platforms
        if references:
            data['references'] = references
        if note:
            data['note'] = note

        response = requests.post(
            '{}/releases'.format(self.uri),
            headers=self.headers,
            json=data,
        )
        release_id = response.json()['id']
        return uuid.UUID(release_id)

    def create_package(self, release_id, name, version):
        """
        Create a package using the REST API

        :param release_id: release id to create the package for
        :param name:
        :param version:
        :return: package id
        """

        response = requests.post(
            '{}/releases/{}/packages'.format(self.uri, release_id),
            headers=self.headers,
            json={
                'name': name,
                'version': version,
            },
        )
        id = response.json()['id']
        return uuid.UUID(id)

    @staticmethod
    def start_release():
        """
        Releases are automatically started when they are created
        """
        pass

    def stop_release(self, release_id):
        """
        Stop a release using the REST API
        """
        response = requests.post(
            '{}/releases/{}/stop'.format(self.uri, release_id),
            headers=self.headers,
        )

        if response.status_code != 204:
            raise OrloServerError(
                "Orlo server returned non-204 status code: {}".format(response.json()))

        return True

    def start_package(self, release_id, package_id):
        """
        Start a package using the REST API

        :param release_id: Release UUID
        :param package_id: Package UUID
        :return:
        """

        response = requests.post(
            '{}/releases/{}/packages/{}/start'.format(
                self.uri, release_id, package_id),
            headers=self.headers,
        )

        if response.status_code != 204:
            raise OrloServerError(
                "Orlo server returned non-204 status code: {}".format(response.json()))

        return True

    def stop_package(self, release_id, package_id,
                     success=True):
        """
        Start a package using the REST API

        :param release_id:
        :return:
        """

        response = requests.post(
            '{}/releases/{}/packages/{}/stop'.format(
                self.uri, release_id, package_id),
            json={
                'success': success,
            },
            headers=self.headers,
        )

        if response.status_code != 204:
            raise OrloServerError(
                "Orlo server returned non-204 status code: {}".format(response.json()))
        return True

