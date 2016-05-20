from __future__ import print_function
import logging
import requests

from .exceptions import OrloClientError, OrloServerError
from .objects import Release, Package

__author__ = 'alforbes'


class OrloClient(object):
    """
    Reference object to our Orlo server

    This object is intended to be a very thin layer to the actual http calls,
    there is very little abstraction. See Release and Package if you want
    more OO-like objects.

    See mock_orlo for a mock-up of this class. Tests other than test_orloclient
    use the mock.
    """

    headers = {'Content-Type': 'application/json'}

    def __init__(self, uri, verify_ssl=True):
        self.logger = logging.getLogger(__name__)
        self.uri = uri
        self.verify_ssl = verify_ssl

    def _expect_200_json_response(self, response, status_code=200):
        """
        Check for an appropriate status code

        :param response response: Requests library response object
        :param int status_code: The expected status_code
        :return dict:
        """
        self.logger.debug("Response {}:\n{}".format(response.status_code, response.text))

        if response.status_code == 204:
            return True
        elif response.status_code == status_code:
            try:
                return response.json()
            except ValueError:
                raise OrloClientError(
                    "Could not decode json from Orlo response:\n{}".format(
                        str(response.text)))
        else:
            msg = "Orlo server returned code {code}:\n{text}".format(
                code=response.status_code, text=response.text)

            if response.status_code in (301, 302):
                # Requests does not redo the post when receiving a redirect
                # Thus, we use allow_redirect=False for POSTs which will result
                # in the redirect appearing here
                raise OrloServerError("Got redirect while attempting to POST")
            elif response.status_code >= 500:
                raise OrloServerError(msg)
            else:
                raise OrloClientError(msg)

    def ping(self):
        response = requests.get(self.uri + '/ping', verify=self.verify_ssl)

        if response.status_code == 200:
            return True
        else:
            return False

    def get_release(self, release_id):
        """
        Fetch a single Release

        :param release_id:
        :return:
        """
        
        response_dict = self.get_release_json(release_id)
        self.logger.debug(response_dict)

        releases_list = [Release(self, r['id']) for r in response_dict['releases']]
        if len(releases_list) > 1:
            raise OrloServerError("Got list of length > 1")

        return releases_list[0]

    def get_releases(self, **kwargs):
        """
        Fetch releases from the orlo API with filters

        http://orlo.readthedocs.org/en/latest/rest.html#get--releases
        :param kwargs: Filters to apply
        """
        self.logger.debug("Entering get_releases")

        if len(kwargs) is 0:
            msg = "Must specify at least one filter for releases"
            raise OrloClientError(msg)

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

        response_dict = self._expect_200_json_response(response)
        releases_list = [Release(self, r['id']) for r in response_dict['releases']]

        return releases_list

    def get_release_json(self, release_id):
        """
        Fetch a releases from the orlo API

        :param release_id:
        :returns dict:
        """
        self.logger.debug("Entering get_releases")
        url = "{url}/releases/{rid}".format(url=self.uri, rid=release_id)

        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        self.logger.debug(response)
        return self._expect_200_json_response(response)

    def create_release(self, user, platforms,
                       team=None, references=None, note=None):
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

        req_url = '{}/releases'.format(self.uri)
        self.logger.debug("Posting to {}:\n{}".format(req_url, data))
        response = requests.post(
            req_url,
            headers=self.headers,
            json=data,
            verify=self.verify_ssl,
            allow_redirects=False,
        )

        self._expect_200_json_response(response)

        release_id = response.json()['id']
        return Release(self, release_id)

    def create_package(self, release, name, version):
        """
        Create a package using the REST API

        :param Release release: release to create the package for
        :param string name: Name of the package
        :param string version: Version of the package
        :return: package id
        """

        response = requests.post(
            '{}/releases/{}/packages'.format(self.uri, release.release_id),
            headers=self.headers,
            json={
                'name': name,
                'version': version,
            },
            verify=self.verify_ssl,
            allow_redirects=False,
        )

        self._expect_200_json_response(response)

        pkg = response.json()
        return Package(release.id, pkg['id'], name, version)

    @staticmethod
    def release_start():
        """
        Releases are automatically started when they are created
        """
        pass

    def release_stop(self, release):
        """
        Stop a release using the REST API

        :param release: Release object
        :returns boolean: Whether or not the release was successfully stopped
        """
        release_id = release.release_id
        response = requests.post(
            '{}/releases/{}/stop'.format(self.uri, release_id),
            headers=self.headers,
            verify=self.verify_ssl,
            allow_redirects=False,
        )

        return self._expect_200_json_response(response, status_code=204)

    def package_start(self, package):
        """
        Start a package using the REST API

        :param Package package: Package object
        :return boolean: Whether or not the package was successfully started
        """

        response = requests.post(
            '{}/releases/{}/packages/{}/start'.format(
                self.uri, package.release_id, package.id),
            headers=self.headers,
            verify=self.verify_ssl,
            allow_redirects=False,
        )

        if response.status_code != 204:
            self.logger.debug(response)
            raise OrloServerError(
                "Orlo server returned non-204 status code: {}".format(response.json()))

        return self._expect_200_json_response(response, status_code=204)

    def package_stop(self, package, success=True):
        """
        Start a package using the REST API

        :param Package package: Package object
        :param boolean success: Whether or not the package was successfully stopped
        :return boolean: Whether or not the package was successfully stopped
        """
        release_id = package.release_id
        package_id = package.id

        response = requests.post(
            '{}/releases/{}/packages/{}/stop'.format(
                self.uri, release_id, package_id),
            json={
                'success': success,
            },
            headers=self.headers,
            verify=self.verify_ssl,
            allow_redirects=False,
        )

        return self._expect_200_json_response(response, status_code=204)

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
        return self._expect_200_json_response(response)

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
        return self._expect_200_json_response(response)

    def deploy_release(self, release_id):
        """
        Send the command to deploy a release

        :param release_id: Release ID to deploy
        :return:
        """
        url = "{url}/releases/{rid}/deploy".format(url=self.uri, rid=release_id)

        response = requests.post(
            url, headers=self.headers, verify=self.verify_ssl,
            allow_redirects=False,
        )
        self.logger.debug(response)

        return self._expect_200_json_response(response)

    def get_versions(self):
        """
        Return a JSON document of all package versions

        :return:
        """
        url = "{url}/info/packages/versions".format(url=self.uri)

        response = requests.get(
            url, headers=self.headers, verify=self.verify_ssl
        )
        self.logger.debug(response)

        return self._expect_200_json_response(response)

