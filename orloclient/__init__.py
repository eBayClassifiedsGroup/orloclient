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

    def __init__(self, uri, requests_verify=True):
        self.logger = logging.getLogger(__name__)
        self.uri = uri
        self.requests_verify = requests_verify

    def ping(self):
        response = requests.get(self.uri + '/ping', verify=self.requests_verify)
        if response.status_code == 200:
            return True
        else:
            return False

    def get_releases(self, release_id=False, **kwargs):
        """
        Fetch releases from the orlo API, optionally filtering

        http://orlo.readthedocs.org/en/latest/rest.html#get--releases
        :param release_id:
        :param kwargs: Filters to apply
        """
        self.logger.debug("Entering get_releases")

        if release_id:
            url = "{url}/releases/{id}".format(url=self.uri, id=release_id)
        else:
            url = "{url}/releases".format(url=self.uri)

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

        if filters:
            url = "{url}?{filters}".format(url=url, filters='&'.join(filters))

        response = requests.get(url, headers=self.headers, verify=self.requests_verify)
        self.logger.debug(response)
        return response.json()

    def create_release(self, user, platforms,
                       team=None,
                       references=None,
                       note=None,
                       ):
        """
        Create a release using the REST API
        :param string user: User performing the release
        :param list platforms: List of strings, platforms being released to
        :param string team: Team responsible for the release
        :param list references: List of strings, external references, e.g. Jira ticket
        :param string note: Free-text field for additional information
        """

        data = {
            'platforms': platforms,
            'user': user,
        }

        if team:
            data['team'] = team
        if references:
            data['references'] = references
        if note:
            data['note'] = note

        response = requests.post(
            '{}/releases'.format(self.uri),
            headers=self.headers,
            json=data,
            verify=self.requests_verify,
        )
        self.logger.debug(response)
        release_id = response.json()['id']
        return uuid.UUID(release_id)

    def create_package(self, release_id, name, version):
        """
        Create a package using the REST API

        :param string release_id: release id to create the package for
        :param string name: Name of the package
        :param string version: Version of the package
        :return: package id
        """

        response = requests.post(
            '{}/releases/{}/packages'.format(self.uri, release_id),
            headers=self.headers,
            json={
                'name': name,
                'version': version,
            },
            verify=self.requests_verify,
        )
        self.logger.debug(response)
        package_id = response.json()['id']
        return uuid.UUID(package_id)

    @staticmethod
    def release_start():
        """
        Releases are automatically started when they are created
        """
        pass

    def release_stop(self, release_id):
        """
        Stop a release using the REST API

        :param uuid.UUID release_id: Release UUID
        :returns boolean: Whether or not the release was successfully stopped
        """
        response = requests.post(
            '{}/releases/{}/stop'.format(self.uri, release_id),
            headers=self.headers,
            verify=self.requests_verify,
        )

        if response.status_code != 204:
            self.logger.debug(response)
            raise OrloServerError(
                "Orlo server returned non-204 status code: {}".format(response.json()))

        return True

    def package_start(self, release_id, package_id):
        """
        Start a package using the REST API

        :param uuid.UUID release_id: Release UUID
        :param uuid.UUID package_id: Package UUID
        :return boolean: Whether or not the package was successfully started
        """

        response = requests.post(
            '{}/releases/{}/packages/{}/start'.format(
                self.uri, release_id, package_id),
            headers=self.headers,
            verify=self.requests_verify,
        )

        if response.status_code != 204:
            self.logger.debug(response)
            raise OrloServerError(
                "Orlo server returned non-204 status code: {}".format(response.json()))

        return True

    def package_stop(self, release_id, package_id,
                     success=True):
        """
        Start a package using the REST API

        :param uuid.UUID release_id: Release UUID
        :param uuid.UUID package_id: Package UUID
        :param boolean success: Whether or not the package was successfully stopped
        :return boolean: Whether or not the package was successfully stopped
        """

        response = requests.post(
            '{}/releases/{}/packages/{}/stop'.format(
                self.uri, release_id, package_id),
            json={
                'success': success,
            },
            headers=self.headers,
            verify=self.requests_verify,
        )

        if response.status_code != 204:
            self.logger.debug(response)
            raise OrloServerError(
                "Orlo server returned non-204 status code: {}".format(response.json()))
        return True

