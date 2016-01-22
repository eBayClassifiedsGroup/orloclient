from __future__ import print_function
from orloclient.config import config
from orloclient.exceptions import OrloClientError, OrloServerError
import logging
import requests
import uuid


def _expect_200_response(response, status_code=200):
    """
    Check for an appropriate status code

    :param response response: Requests library response object
    :param int status_code: The expected status_code
    :return:
    """

    if response.status_code == 204:
        return True

    if response.status_code == status_code:
        try:
            return response.json()
        except ValueError:
            raise OrloClientError("Could not decode json from Orlo response:\n{}".format(
                str(response.text)
            ))

    msg = "Orlo server returned code {code}:\n{text}".format(
            code=response.status_code, text=response.text)

    if response.status_code > 500:
        raise OrloServerError(msg)
    else:
        raise OrloClientError(msg)


class Orlo(object):
    """
    Reference object to our Orlo server
    """

    headers = {'Content-Type': 'application/json'}

    def __init__(self, uri, verify_ssl=True):
        self.logger = logging.getLogger(__name__)
        self.uri = uri
        self.verify_ssl = verify_ssl

    def ping(self):
        response = requests.get(self.uri + '/ping', verify=self.verify_ssl)

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
            f = "{}={}".format(key, kwargs[key])
            self.logger.debug("Append filter {}".format(f))
            filters.append(f)

        if filters:
            url = "{url}?{filters}".format(url=url, filters='&'.join(filters))

        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        self.logger.debug(response)
        return _expect_200_response(response)

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
            verify=self.verify_ssl,
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
            verify=self.verify_ssl,
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
            verify=self.verify_ssl,
        )

        return _expect_200_response(response, status_code=204)

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
            verify=self.verify_ssl,
        )

        if response.status_code != 204:
            self.logger.debug(response)
            raise OrloServerError(
                    "Orlo server returned non-204 status code: {}".format(response.json()))

        return _expect_200_response(response, status_code=204)

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
            verify=self.verify_ssl,
        )

        return _expect_200_response(response, status_code=204)

    def get_info(self, field, name=None, platform=None):
        """
        Fetch from the /info endpoint

        Field is required, as /info just has links and isn't useful

        :param field: The "field" (table?) we are looking at, i.e. user/team/package/platform
        :param name: The subject, e.g the user name / team name / package name
        :param platform: Filter by platform
        :return:
        """

        url_path = {
            'uri': self.uri,
            'field': field if field else '',
            'name': '/' + name if name else '',
        }

        url_query = {'platform': platform} if platform else {}

        response = requests.get(
            '{uri}/info/{field}{name}'.format(**url_path), params=url_query
        )
        return response.json()

    def get_stats(self, field=None, name=None, platform=None, stime=None, ftime=None):
        """
        Fetch from the /stats endpoint

        Field is optional, as /stats presents global stats

        :param field: The "field" (table?) we are looking at, i.e. user/team/package/platform
        :param name: The subject, e.g the user name / team name / package name
        :param platform: Filter by platform
        :param stime: Lower-bound start time filter
        :param ftime: Upper-bound start time filter
        :return:
        """

        url_path = {
            'uri': self.uri,
            'field': '/' + field if field else '',
            'name': '/' + name if name else '',
        }

        url_query = {}
        for var in ['platform', 'stime', 'ftime']:
            url_query[var] = eval(var)

        response = requests.get(
            '{uri}/stats{field}{name}'.format(**url_path), params=url_query
        )
        return response.json()
