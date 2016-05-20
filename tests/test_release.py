from __future__ import print_function
from tests import OrloClientTest
from orloclient.mock_orlo import MockOrloClient
from orloclient import Release, Package
from orloclient.exceptions import OrloClientError
import arrow
import uuid

__author__ = 'alforbes'

client = MockOrloClient('http://dummy.example.com')

"""
Tests of the Release class use the mock client
"""


class TestRelease(OrloClientTest):
    def setUp(self):
        self.release_id = client.example_release_dict['id']
        self.release = Release(client, self.release_id)

    def test_release_id(self):
        """
        Test that the release id returned matches the one from the mock
        and is a UUID
        """
        self.assertIsInstance(self.release.uuid, uuid.UUID)
        self.assertEqual(self.release.uuid, uuid.UUID(self.release_id))

    def test_release_bad_attribute(self):
        """
        Test that we get KeyError when a bad attribute is requested
        """
        with self.assertRaises(OrloClientError):
            return self.release.bad_attribute_19847

    def test_release_stime(self):
        """
        Test that stime is cast to an arrow object
        """
        self.assertIsInstance(self.release.stime,
                              arrow.arrow.Arrow)
        self.assertEqual(self.release.stime,
                         arrow.get(client.example_release_dict['stime']))

    def test_release_ftime(self):
        self.assertIsInstance(self.release.ftime,
                              arrow.arrow.Arrow)
        self.assertEqual(self.release.ftime,
                         arrow.get(client.example_release_dict['ftime']))

    def test_release_meta(self):
        self.assertIsInstance(self.release.metadata, dict)
        self.assertEqual(self.release.metadata,
                         client.example_release_dict['metadata'])

    def test_release_platforms(self):
        self.assertIsInstance(self.release.platforms, list)
        self.assertEqual(self.release.platforms,
                         client.example_release_dict['platforms'])

    def test_release_duration_int(self):
        self.assertIsInstance(self.release.duration, int)
        self.assertEqual(self.release.duration,
                         client.example_release_dict['duration'])

    def test_release_when_value_none(self):
        """
        Test that we get NoneType when a value is None
        """
        client.example_release_dict['none_attribute'] = None
        self.assertIs(self.release.none_attribute, None)

    def test_release_packages_list(self):
        """
        Test we get a list when calling the packages attribute
        """
        self.assertIsInstance(self.release.packages, list)

    def test_release_deploy(self):
        """
        Test the deploy release function returns
        """
        self.assertIs(True, self.release.deploy())

    def test_add_package(self):
        """
        Test adding a package
        """
        self.assertIsInstance(
            self.release.add_package(
                'test-package', '1.0.0'),
            Package
        )
