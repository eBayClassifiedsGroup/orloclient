from __future__ import print_function
import logging
import json
from .base_client import BaseClient

from .exceptions import ClientError, ServerError, ConnectionError
from .objects import Release, Package

__author__ = 'alforbes'
logger = logging.getLogger(__name__)



class OrloClient(BaseClient):
    """
    Reference object to our Orlo server

    This object is intended to be a very thin layer to the actual http calls,
    there is very little abstraction. See Release and Package if you want
    more OO-like objects.

    See mock_orlo for a mock-up of this class. Tests other than test_orloclient
    use the mock.
    """

    def __init__(self, uri, timeout=10, verify_ssl=True):
        super(OrloClient, self).__init__(
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        self.uri = uri

    def _expect_200_json_response(self, response, status_code=200):
        """
        Check for an appropriate status code

        :param response response: Requests library response object
        :param int status_code: The expected status_code
        :return dict:
        """
        logger.debug("Response {}:\n{}".format(
            response.status_code, response.text))

        if response.status_code == 204:
            return True
        elif response.status_code == status_code:
            try:
                return response.json()
            except ValueError:
                raise ClientError(
                    "Could not decode json from Orlo response:\n{}".format(
                        str(response.text)))
        else:
            msg = "Orlo server returned code {code}:\n{text}".format(
                code=response.status_code, text=response.text)

            if response.status_code in (301, 302):
                # Requests does not redo the post when receiving a redirect
                # Thus, we use allow_redirect=False for POSTs which will result
                # in the redirect appearing here
                raise ServerError("Got redirect while attempting to POST")
            elif response.status_code >= 500:
                raise ServerError(msg)
            else:
                raise ClientError(msg)

    def ping(self):
        response = self._get(self.uri + '/ping')

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
        logger.debug(response_dict)

        releases_list = [
            Release(self, r['id']) for r in response_dict['releases']
        ]
        if len(releases_list) > 1:
            raise ServerError("Got list of length > 1")

        return releases_list[0]

    def get_releases(self, **kwargs):
        """
        Fetch releases from the orlo API with filters

        http://orlo.readthedocs.org/en/latest/rest.html#get--releases
        :param kwargs: Filters to apply
        """
        logger.debug("Entering get_releases")

        if len(kwargs) is 0:
            msg = "Must specify at least one filter for releases"
            raise ClientError(msg)

        url = "{url}/releases".format(url=self.uri)

        filters = []

        for key in kwargs:
            f = "{}={}".format(key, kwargs[key])
            logger.debug("Append filter {}".format(f))
            filters.append(f)

        if filters:
            url = "{url}?{filters}".format(url=url, filters='&'.join(filters))

        response = self._get(url)
        logger.debug(response)

        response_dict = self._expect_200_json_response(response)
        releases_list = [Release(self, r['id']) for r in response_dict['releases']]

        return releases_list

    def get_release_json(self, release_id):
        """
        Fetch a release from the orlo API

        :param release_id:
        :returns dict:
        """
        logger.debug("Entering get_release_json")
        url = "{url}/releases/{rid}".format(url=self.uri, rid=release_id)

        response = self._get(url)
        logger.debug(response)
        return self._expect_200_json_response(response)

    def get_package_json(self, package_id):
        """
        Fetch a package from the orlo API

        :param package_id:
        :return:
        """
        logger.debug("Entering get_package_json")
        url = "{url}/packages/{pid}".format(url=self.uri, pid=package_id)

        response = self._get(url)
        logger.debug(response)
        return self._expect_200_json_response(response)

    def create_release(self, user, platforms,
                       team=None, references=None, note=None, metadata=None):
        """
        Create a release using the REST API
        :param string user: User performing the release
        :param list platforms: List of strings, platforms being released to
        :param string team: Team responsible for the release
        :param list references: List of strings, external references, e.g. Jira ticket
        :param string note: Free-text field for additional information
        :param dict metadata: dictionary containing arbitrary data
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
        if metadata:
            data['metadata'] = metadata

        req_url = '{}/releases'.format(self.uri)
        logger.debug("Posting to {}:\n{}".format(req_url, data))
        response = self._post(
            req_url,
            json=data,
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

        response = self._post(
            '{}/releases/{}/packages'.format(self.uri, release.release_id),
            json={
                'name': name,
                'version': version,
            },
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
        response = self._post(
            '{}/releases/{}/stop'.format(self.uri, release_id),
            allow_redirects=False,
        )

        return self._expect_200_json_response(response, status_code=204)

    def get_package(self, package_id):
        """
        Fetch a single Package

        :param package_id:
        """

        response_dict = self.get_package_json(package_id)
        logger.debug('Response Dict:\n{}'.format(
            json.dumps(response_dict, indent=2)))

        packages_list = [
            Package(p['release_id'], p['id'], p['name'], p['version'])
            for p in response_dict['packages']
            ]
        if len(packages_list) > 1:
            raise ServerError("Got list of length > 1")

        return packages_list[0]

    def get_packages(self, **kwargs):
        """
        Fetch packages from the orlo API with filters

        http://orlo.readthedocs.org/en/latest/rest.html#get--packages
        :param kwargs: Filters to apply
        """
        logger.debug("Entering get_packages")

        if len(kwargs) is 0:
            msg = "Must specify at least one filter for packages"
            raise ClientError(msg)

        url = "{url}/packages".format(url=self.uri)

        filters = []

        for key in kwargs:
            f = "{}={}".format(key, kwargs[key])
            logger.debug("Append filter {}".format(f))
            filters.append(f)

        if filters:
            url = "{url}?{filters}".format(url=url, filters='&'.join(filters))

        response = self._get(url)
        logger.debug(response)

        response_dict = self._expect_200_json_response(response)
        packages_list = [
            Package(None, p['id'], p['name'], p['version'])
            for p in response_dict['packages']
        ]

        return packages_list

    def package_start(self, package):
        """
        Start a package using the REST API

        :param Package package: Package object
        :return boolean: Whether or not the package was successfully started
        """

        response = self._post(
            '{}/releases/{}/packages/{}/start'.format(
                self.uri, package.release_id, package.id),
            allow_redirects=False,
        )

        if response.status_code != 204:
            logger.debug(response)
            raise ServerError(
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

        response = self._post(
            '{}/releases/{}/packages/{}/stop'.format(
                self.uri, release_id, package_id),
            json={
                'success': success,
            },
            allow_redirects=False,
        )

        return self._expect_200_json_response(response, status_code=204)


    def package_add_results(self, package, results):
        """
        Add results to a package

        :param Package package: Package object
        :param String results: The results string that you want to add to the package
        :return boolean: Whether or not the package was successfully updated
        """
        release_id = package.release_id
        package_id = package.id

        response = self._post(
            '{}/releases/{}/packages/{}/results'.format(
                self.uri, release_id, package_id),
            json={
                'content': results,
            },
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

        response = self._get(
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

        response = self._get(
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

        response = self._post(url, allow_redirects=False)
        logger.debug(response)

        return self._expect_200_json_response(response)

    def get_versions(self):
        """
        Return a JSON document of all package versions

        :return:
        """
        url = "{url}/info/packages/versions".format(url=self.uri)

        response = self._get(url)
        logger.debug(response)

        return self._expect_200_json_response(response)
