from __future__ import print_function
from tests import OrloClientTest
from orloclient.mock_orlo import MockOrloClient
from orloclient import Package, Release
from orloclient.exceptions import OrloClientError
import arrow
import uuid

__author__ = 'alforbes'

client = MockOrloClient('http://dummy.example.com')


class TestPackage(OrloClientTest):
    def setUp(self):
        self.rid = client.example_release_dict['id']
        self.pid = client.example_package_dict['id']
        self.release = Release(client, self.rid)
        self.package = Package(self.release, self.pid)

    def test_package_id(self):
        """
        Test that the package id returned matches the one from the mock and is a UUID
        """
        self.assertIsInstance(self.package.id, uuid.UUID)
        self.assertEqual(self.package.id, uuid.UUID(self.pid))

    def test_package_bad_attribute(self):
        """
        Test that we get KeyError when a bad attribute is requested
        """
        with self.assertRaises(OrloClientError):
            return self.package.bad_attribute_19846

    def test_package_stime(self):
        """
        Test that stime is cast to an arrow object
        """
        self.assertIsInstance(self.package.stime,
                              arrow.arrow.Arrow)
        self.assertEqual(self.package.stime,
                         arrow.get(client.example_package_dict['stime']))

    def test_package_ftime(self):
        self.assertIsInstance(self.package.ftime,
                              arrow.arrow.Arrow)
        self.assertEqual(self.package.ftime,
                         arrow.get(client.example_package_dict['ftime']))

    def test_package_duration_int(self):
        self.assertIsInstance(self.package.duration, int)
        self.assertEqual(self.package.duration,
                         client.example_package_dict['duration'])

    def test_package_when_value_none(self):
        """
        Test that we get NoneType when a value is None
        """
        client.example_package_dict['none_attribute'] = None
        self.assertIs(self.package.none_attribute, None)
