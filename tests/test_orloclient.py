from __future__ import print_function
import httpretty
import json
import uuid
from unittest import TestCase
from orloclient import Orlo
from orloclient import OrloClientError, OrloServerError

__author__ = 'alforbes'

'''
test_orloclient.py

This file mocks the request library, hence it is a test of the client only, and not its
integration with the orlo server
'''


class OrloClientTest(TestCase):
    """
    Parent method for Orlo client tests

    Constants in this class are test parameters for Orlo methods
    """
    NOTE = 'test note'
    PACKAGE_ID = uuid.uuid4()
    PLATFORMS = ['test_platform']
    REFERENCES = ['test_reference']
    RELEASE_ID = uuid.uuid4()
    TEAM = 'test_team'
    URI = 'http://localhost:1337'
    USER = 'test_user'

    def setUp(self):
        self.orlo = Orlo(self.URI)

    @httpretty.activate
    def test_ping(self):
        httpretty.register_uri(
                httpretty.GET, "http://localhost:1337/ping",
                body="pong",
                status=200,
        )

        self.assertEqual(self.orlo.ping(), True)


class GetReleasesTest(OrloClientTest):
    DUMMY_JSON = {"message": "dummy json"}
    DUMMY_JSON_S = str(DUMMY_JSON).replace("'", '"')

    @httpretty.activate
    def test_get_release_with_id(self):
        """
        Test getting a release by ID
        """
        httpretty.register_uri(
                httpretty.GET, '{}/releases/{}'.format(self.URI, self.RELEASE_ID),
                body=self.DUMMY_JSON_S,
                status=200,
        )

        response = self.orlo.get_releases(release_id=self.RELEASE_ID)
        self.assertEqual(response['message'], self.DUMMY_JSON['message'])

    @httpretty.activate
    def test_get_releases(self):
        """
        Test getting all releases
        """
        httpretty.register_uri(
                httpretty.GET, '{}/releases'.format(self.URI, self.RELEASE_ID),
                body=self.DUMMY_JSON_S,
                status=200,
        )

        response = self.orlo.get_releases()
        self.assertEqual(response['message'], self.DUMMY_JSON['message'])

    @httpretty.activate
    def test_get_releases_filter(self):
        """
        Test that we pass through a filter to the request
        """
        httpretty.register_uri(
                httpretty.GET, '{}/releases?user=foo'.format(self.URI, self.RELEASE_ID),
                body=self.DUMMY_JSON_S,
                status=200,
        )

        response = self.orlo.get_releases(user='foo')
        self.assertEqual(response['message'], self.DUMMY_JSON['message'])


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
                body='{{"id": "{}"}}'.format(self.RELEASE_ID),
                content_type='application/json',
        )

        self.assertEqual(
                self.orlo.create_release(self.USER, self.PLATFORMS),
                self.RELEASE_ID,
        )

    @httpretty.activate
    def test_create_release_with_team(self):
        """
        Test creating a release with the team argument added
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases'.format(self.URI),
                status=200,
                body='{{"id": "{}"}}'.format(self.RELEASE_ID),
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
                body='{{"id": "{}"}}'.format(self.RELEASE_ID),
                content_type='application/json',
        )

        self.orlo.create_release(self.USER, self.PLATFORMS, references=self.REFERENCES)

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
                body='{{"id": "{}"}}'.format(self.RELEASE_ID),
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
        httpretty.register_uri(
                httpretty.POST, '{}/releases/{}/stop'.format(self.URI, self.RELEASE_ID),
                status=204,
                content_type='application/json',
        )

        self.assertEqual(self.orlo.release_stop(self.RELEASE_ID), True)


class WorkflowTest(OrloClientTest):
    """
    Test the remaining release workflow methods
    """

    @httpretty.activate
    def test_package_start(self):
        """
        Test package_start
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases/{}/packages/{}/start'.format(
                        self.URI, self.RELEASE_ID, self.PACKAGE_ID),
                status=204,
                content_type='application/json',
        )

        self.assertEqual(
                self.orlo.package_start(self.RELEASE_ID, self.PACKAGE_ID),
                True)

    @httpretty.activate
    def test_package_stop(self):
        """
        Test package_stop
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases/{}/packages/{}/stop'.format(
                        self.URI, self.RELEASE_ID, self.PACKAGE_ID),
                status=204,
                content_type='application/json',
        )

        self.assertEqual(
                self.orlo.package_stop(self.RELEASE_ID, self.PACKAGE_ID),
                True)

    @httpretty.activate
    def test_package_stop_with_success_true(self):
        """
        Test package_stop with success=True
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases/{}/packages/{}/stop'.format(
                        self.URI, self.RELEASE_ID, self.PACKAGE_ID),
                status=204,
                content_type='application/json',
        )

        self.orlo.package_stop(self.RELEASE_ID, self.PACKAGE_ID, success=True)

        body = json.loads(httpretty.last_request().body)
        self.assertEqual(True, body['success'])

    @httpretty.activate
    def test_package_stop_with_success_false(self):
        """
        Test package_stop with success=False
        """
        httpretty.register_uri(
                httpretty.POST, '{}/releases/{}/packages/{}/stop'.format(
                        self.URI, self.RELEASE_ID, self.PACKAGE_ID),
                status=204,
                content_type='application/json',
        )

        self.orlo.package_stop(self.RELEASE_ID, self.PACKAGE_ID, success=False)

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
                httpretty.GET, '{}/releases/{}'.format(self.URI, self.RELEASE_ID),
                status=404,
                content_type='application/json',
        )
        self.assertRaises(OrloClientError, self.orlo.get_releases, self.RELEASE_ID)

    @httpretty.activate
    def test_error_invalid_json(self):
        """
        Test that we return the appropriate error when we get invalid json
        """

        httpretty.register_uri(
                httpretty.GET, '{}/releases/{}'.format(self.URI, self.RELEASE_ID),
                status=200,
                body='{"foo": "bar"} this is not valid json',
        )
        self.assertRaises(OrloClientError, self.orlo.get_releases, self.RELEASE_ID)


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
            httpretty.GET, '{}/info/users?platform={}'.format(self.URI, 'platform_one'),
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
        self.assertEqual(httpretty.last_request().querystring, {'platform': ['platformOne']})
        self.assertEqual(self.DOC, result)
