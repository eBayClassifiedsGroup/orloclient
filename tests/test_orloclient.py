from __future__ import print_function
import httpretty
import json
import uuid
from unittest import TestCase
from orloclient import Orlo

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
