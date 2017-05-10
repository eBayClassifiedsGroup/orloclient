from __future__ import print_function
import httpretty
import json
from orloclient import ClientError, ServerError
from tests import OrloClientTest
import uuid
import logging

__author__ = 'alforbes'

'''
test_orloclient.py

This file mocks the request library, hence it is a test of the client only, and
not its integration with the orlo server
'''

logging.basicConfig(level=logging.DEBUG)


class TestOrloBase(OrloClientTest):
    """
    Base functionality
    """

    @httpretty.activate
    def test_ping(self):
        httpretty.register_uri(
                httpretty.GET, "http://localhost:1337/ping",
                body="pong",
                status=200,
        )

        self.assertEqual(self.orlo.ping(), True)


class TestGetReleases(OrloClientTest):
    DUMMY_JSON = {"message": "dummy json"}
    # Raw string for httpretty to return:
    DUMMY_JSON_S = str(DUMMY_JSON).replace("'", '"')

    RELEASE_JSON = {
        'releases': [
            {'id': str(uuid.uuid4())}
        ]}
    # Raw string for httpretty to return:
    RELEASE_JSON_S = str(RELEASE_JSON).replace("'", '"')

    @httpretty.activate
    def test_get_release_json_with_id(self):
        """
        Test that we get back the correct raw json when calling get_release_json
        """
        httpretty.register_uri(
                httpretty.GET,
                '{}/releases/{}'.format(self.URI, self.RELEASE.release_id),
                body=self.DUMMY_JSON_S,
                status=200,
        )

        response = self.orlo.get_release_json(self.RELEASE.release_id)
        self.assertEqual(response['message'], self.DUMMY_JSON['message'])

    @httpretty.activate
    def test_get_release(self):
        """
        Test getting a release by ID

        Would probably depend on the above json test passing.
        """
        rid = self.RELEASE_JSON['releases'][0]['id']
        httpretty.register_uri(
            httpretty.GET, '{}/releases/{}'.format(self.URI, rid),
            body=self.RELEASE_JSON_S,
            status=200,
        )

        result = self.orlo.get_release(rid)
        self.assertEqual(result.id, str(rid))

    @httpretty.activate
    def test_get_releases(self):
        """
        Test getting releases
        """
        httpretty.register_uri(
                httpretty.GET,
                '{}/releases?foo=bar'.format(self.URI, self.RELEASE.release_id),
                body=self.RELEASE_JSON_S,
                status=200,
        )

        release_list = self.orlo.get_releases(foo='bar')
        self.assertEqual(release_list[0].id, self.RELEASE_JSON['releases'][0]['id'])

    def test_get_releases_unfiltered_raises(self):
        """
        Test that get/releases without a filter raises OrloClientError
        """
        with self.assertRaises(ClientError):
            self.orlo.get_releases()

    @httpretty.activate
    def test_get_releases_filter(self):
        """
        Test that we pass through a filter to the request

        If the argument user=foo doesn't make it into the request this test will fail
        """
        httpretty.register_uri(
            httpretty.GET, '{}/releases'.format(self.URI),
            body=self.RELEASE_JSON_S,
            status=200,
        )

        self.orlo.get_releases(user='test_string')
        self.assertEqual(
            httpretty.last_request().querystring['user'],
            ['test_string']
        )


class TestGetPackages(OrloClientTest):
    DUMMY_JSON = {"message": "dummy json"}
    # Raw string for httpretty to return:
    DUMMY_JSON_S = str(DUMMY_JSON).replace("'", '"')

    PACKAGE_JSON = {
        'packages': [
            {
                'id': str(uuid.uuid4()),
                'release_id': str(uuid.uuid4()),
                'name': 'package-one',
                'version': '1.0',
            }
        ]}
    # Raw string for httpretty to return:
    PACKAGE_JSON_S = str(PACKAGE_JSON).replace("'", '"')

    @httpretty.activate
    def test_get_package_json_with_id(self):
        """
        Test that we get back the correct raw json when calling get_package_json
        """
        httpretty.register_uri(
            httpretty.GET,
            '{}/packages/{}'.format(self.URI, self.PACKAGE.id),
            body=self.DUMMY_JSON_S,
            status=200,
        )

        response = self.orlo.get_package_json(self.PACKAGE.id)
        self.assertEqual(response['message'], self.DUMMY_JSON['message'])

    @httpretty.activate
    def test_get_package(self):
        """
        Test getting a package by ID

        Would probably depend on the above json test passing.
        """
        rid = self.PACKAGE_JSON['packages'][0]['id']
        httpretty.register_uri(
            httpretty.GET, '{}/packages/{}'.format(self.URI, rid),
            body=self.PACKAGE_JSON_S,
            status=200,
        )

        result = self.orlo.get_package(rid)
        self.assertEqual(result.id, str(rid))

    @httpretty.activate
    def test_get_package_release_id_not_None(self):
        """
        Test getting a package by ID

        Would probably depend on the above json test passing.
        """
        rid = self.PACKAGE_JSON['packages'][0]['id']
        httpretty.register_uri(
            httpretty.GET, '{}/packages/{}'.format(self.URI, rid),
            body=self.PACKAGE_JSON_S,
            status=200,
        )

        result = self.orlo.get_package(rid)
        print(result.to_dict())
        self.assertIsNotNone(result.release_id)

    @httpretty.activate
    def test_get_packages(self):
        """
        Test getting packages
        """
        httpretty.register_uri(
            httpretty.GET,
            '{}/packages?foo=bar'.format(self.URI, self.PACKAGE.id),
            body=self.PACKAGE_JSON_S,
            status=200,
        )

        package_list = self.orlo.get_packages(foo='bar')
        self.assertEqual(package_list[0].id, self.PACKAGE_JSON['packages'][0]['id'])

    def test_get_packages_unfiltered_raises(self):
        """
        Test that get/packages without a filter raises OrloClientError
        """
        with self.assertRaises(ClientError):
            self.orlo.get_packages()

    @httpretty.activate
    def test_get_packages_filter(self):
        """
        Test that we pass through a filter to the request

        If the argument user=foo doesn't make it into the request this test will fail
        """
        httpretty.register_uri(
            httpretty.GET, '{}/packages'.format(self.URI),
            body=self.PACKAGE_JSON_S,
            status=200,
        )

        self.orlo.get_packages(user='test_string')
        self.assertEqual(
            httpretty.last_request().querystring['user'],
            ['test_string']
        )


class CreateReleaseTest(OrloClientTest):
    """
    Testing the create_release function
    """

    @httpretty.activate
    def test_create_release(self):
        """
        Test creating a release with minimal arguments
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases'.format(self.URI),
                status=200,
                body='{{"id": "{}"}}'.format(self.RELEASE.release_id),
                content_type='application/json',
        )
        release = self.orlo.create_release(self.USER, self.PLATFORMS)

        self.assertEqual(
            uuid.UUID(release.release_id),
            self.RELEASE.uuid,
        )

    @httpretty.activate
    def test_create_release_with_team(self):
        """
        Test creating a release with the team argument added
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases'.format(self.URI),
                status=200,
                body='{{"id": "{}"}}'.format(self.RELEASE.release_id),
                content_type='application/json',
        )

        self.orlo.create_release(self.USER, self.PLATFORMS, team=self.TEAM)

        body = json.loads(httpretty.last_request().body)
        self.assertEqual(self.TEAM, body['team'])

    @httpretty.activate
    def test_create_release_with_references(self):
        """
        Test creating a release with the references argument added
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases'.format(self.URI),
                status=200,
                body='{{"id": "{}"}}'.format(self.RELEASE.release_id),
                content_type='application/json',
        )

        self.orlo.create_release(
            self.USER, self.PLATFORMS, references=self.REFERENCES)

        body = json.loads(httpretty.last_request().body)
        self.assertEqual(self.REFERENCES, body['references'])

    @httpretty.activate
    def test_create_release_with_note(self):
        """
        Test creating a release with the team argument added
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases'.format(self.URI),
                status=200,
                body='{{"id": "{}"}}'.format(self.RELEASE.release_id),
                content_type='application/json',
        )

        self.orlo.create_release(self.USER, self.PLATFORMS, note=self.NOTE)

        body = json.loads(httpretty.last_request().body)
        self.assertEqual(self.NOTE, body['note'])


class ReleaseStopTest(OrloClientTest):
    """
    Test stopping a release
    """

    @httpretty.activate
    def test_release_stop(self):
        """
        Test release_stop
        """
        url = '{}/releases/{}/stop'.format(self.URI, self.RELEASE.release_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            status=204,
            content_type='application/json',
        )

        self.assertEqual(self.orlo.release_stop(self.RELEASE), True)


class WorkflowTest(OrloClientTest):
    """
    Test the remaining release workflow methods
    """

    @httpretty.activate
    def test_package_start(self):
        """
        Test package_start
        """
        url = '{}/releases/{}/packages/{}/start'.format(
            self.URI, self.PACKAGE.release_id, self.PACKAGE.id)
        httpretty.register_uri(
            httpretty.POST, url,
            status=204,
            content_type='application/json',
        )

        self.assertEqual(
            self.orlo.package_start(self.PACKAGE),
            True)

    @httpretty.activate
    def test_package_stop(self):
        """
        Test package_stop
        """
        httpretty.register_uri(
            httpretty.POST, '{}/releases/{}/packages/{}/stop'.format(
                    self.URI, self.PACKAGE.release_id, self.PACKAGE.id),
            status=204,
            content_type='application/json',
        )

        self.assertEqual(
            self.orlo.package_stop(self.PACKAGE), True)

    @httpretty.activate
    def test_package_add_results(self):
        """
        Test package_add_results
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases/{}/packages/{}/results'.format(
                        self.URI, self.PACKAGE.release_id, self.PACKAGE.id),
                status=204,
                content_type='application/json',
        )

        self.assertEqual(
                self.orlo.package_add_results(self.PACKAGE, results='test results'), True)


    @httpretty.activate
    def test_package_stop_with_success_true(self):
        """
        Test package_stop with success=True
        """
        httpretty.register_uri(
            httpretty.POST, '{}/releases/{}/packages/{}/stop'.format(
                self.URI, self.PACKAGE.release_id, self.PACKAGE.id),
            status=204,
            content_type='application/json',
        )

        self.orlo.package_stop(self.PACKAGE, success=True)

        body = json.loads(httpretty.last_request().body)
        self.assertEqual(True, body['success'])

    @httpretty.activate
    def test_package_stop_with_success_false(self):
        """
        Test package_stop with success=False
        """
        httpretty.register_uri(
            httpretty.POST, '{}/releases/{}/packages/{}/stop'.format(
                self.URI, self.PACKAGE.release_id, self.PACKAGE.id),
            status=204,
            content_type='application/json',
        )

        self.orlo.package_stop(self.PACKAGE, success=False)

        body = json.loads(httpretty.last_request().body)
        self.assertEqual(False, body['success'])


class ErrorTest(OrloClientTest):
    """
    Test error conditions
    """

    @httpretty.activate
    def test_error_404(self):
        """
        Test that an OrloClient error is raised on 404
        """

        httpretty.register_uri(
                httpretty.GET,
                '{}/releases/{}'.format(self.URI, self.RELEASE.release_id),
                status=404,
                content_type='application/json',
        )
        self.assertRaises(
            ClientError, self.orlo.get_release, self.RELEASE.release_id)

    @httpretty.activate
    def test_error_invalid_json(self):
        """
        Test that we return the appropriate error when we get invalid json
        """

        httpretty.register_uri(
                httpretty.GET,
                '{}/releases/{}'.format(self.URI, self.RELEASE.release_id),
                status=200,
                body='{"foo": "bar"} this is not valid json',
        )
        self.assertRaises(
            ClientError, self.orlo.get_release, self.RELEASE.release_id)


class InfoTest(OrloClientTest):
    """
    Test the /info functions
    """
    DOC = {"user_one": {"releases": 100}}

    @httpretty.activate
    def test_info_users(self):
        """
        Test info/users
        """

        httpretty.register_uri(
                httpretty.GET, '{}/info/users'.format(self.URI),
                status=200,
                content_type='application/json',
                body=json.dumps(self.DOC)
        )

        result = self.orlo.get_info('users')
        self.assertEqual(self.DOC, result)

    @httpretty.activate
    def test_info_users_with_username(self):
        """
        Test info/users/username
        """

        httpretty.register_uri(
            httpretty.GET, '{}/info/users/{}'.format(self.URI, 'user_one'),
            status=200,
            content_type='application/json',
            body=json.dumps(self.DOC)
        )

        result = self.orlo.get_info('users', name='user_one')
        self.assertEqual(self.DOC, result)

    @httpretty.activate
    def test_info_users_with_platform(self):
        """
        Test /info/users?platform
        """

        httpretty.register_uri(
            httpretty.GET,
            '{}/info/users?platform={}'.format(self.URI, 'platform_one'),
            status=200,
            content_type='application/json',
            body=json.dumps(self.DOC)
        )

        result = self.orlo.get_info('users', platform='platform_one')
        self.assertEqual(self.DOC, result)


class StatsTest(OrloClientTest):
    """
    Test the /stats functions
    """
    DOC = {"subject": {
        "releases": {
            "normal": {
                "failed": 1,
                "successful": 2,
            },
            "rollback": {
                "failed": 1,
                "successful": 2,
            },
            "total": {
                "failed": 1,
                "successful": 2,
            }
        }}}

    @httpretty.activate
    def test_stats(self):
        """
        Test /stats
        """
        httpretty.register_uri(
            httpretty.GET, '{}/stats'.format(self.URI),
            status=200,
            content_type='application/json',
            body=json.dumps(self.DOC)
        )

        result = self.orlo.get_stats()
        self.assertEqual(httpretty.last_request().path, '/stats')
        self.assertEqual(self.DOC, result)

    @httpretty.activate
    def test_stats_with_field(self):
        """
        Test /stats
        """
        httpretty.register_uri(
            httpretty.GET, '{}/stats/user'.format(self.URI),
            status=200,
            content_type='application/json',
            body=json.dumps(self.DOC)
        )

        result = self.orlo.get_stats(field='user')
        self.assertEqual(httpretty.last_request().path, '/stats/user')
        self.assertEqual(self.DOC, result)

    @httpretty.activate
    def test_stats_with_field_and_name(self):
        """
        Test /stats
        """
        httpretty.register_uri(
            httpretty.GET, '{}/stats/user/userOne'.format(self.URI),
            status=200,
            content_type='application/json',
            body=json.dumps(self.DOC)
        )

        result = self.orlo.get_stats(field='user', name='userOne')
        self.assertEqual(httpretty.last_request().path, '/stats/user/userOne')
        self.assertEqual(self.DOC, result)

    @httpretty.activate
    def test_stats_with_field_and_query(self):
        """
        Test /stats
        """
        httpretty.register_uri(
            httpretty.GET, '{}/stats/user?platform=platformOne'.format(self.URI),
            status=200,
            content_type='application/json',
            body=json.dumps(self.DOC)
        )

        result = self.orlo.get_stats(field='user', platform='platformOne')
        self.assertEqual(
            httpretty.last_request().querystring, {'platform': ['platformOne']})
        self.assertEqual(self.DOC, result)


class DeployTest(OrloClientTest):
    @httpretty.activate
    def test_deploy(self):
        """
        Test /release/{rid}/deploy
        """
        rid = uuid.uuid4()
        httpretty.register_uri(
            httpretty.POST, '{}/releases/{}/deploy'.format(
                self.URI,
                rid),
            status=204,
            content_type='application/json',
        )

        result = self.orlo.deploy_release(rid)
        self.assertEqual(True, result)


class VersionsTest(OrloClientTest):
    @httpretty.activate
    def test_version(self):
        """
        Test /versions
        """
        expected = {"package_one": "1.2.3"}
        httpretty.register_uri(
            httpretty.GET, '{}/info/packages/versions'.format(self.URI),
            status=200,
            content_type='application/json',
            body=json.dumps(expected)
        )

        result = self.orlo.get_versions()
        self.assertEqual(expected, result)
