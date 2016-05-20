from __future__ import print_function
from orloclient.mock_orlo import MockOrloClient
from orloclient import OrloClient, Release, Package
from unittest import TestCase
import uuid
import json

__author__ = 'alforbes'

excluded_functions = ['release_start']  # Just a stub anyway


def get_callables(obj):
    """
    List the callable functions in the OrloClient object

    :param obj:
    :return:
    """
    c = []
    for attribute in dir(obj):
        if attribute.startswith("_") \
                or attribute in excluded_functions:
            continue
        ref = getattr(obj, attribute)
        if callable(ref):
            c.append(attribute)
    return c


class TestMockOrlo(TestCase):
    """
    Ensure that the mock is updated whenever the client changes...
    """

    functions = get_callables(OrloClient)

    def setUp(self):
        self.mock_client = MockOrloClient(uri='http://dummy')

    def test_attributes(self):
        """
        Compare the attributes of OrloClient and MockOrlo
        """
        for f in self.functions:
            self.assertIn(f, dir(self.mock_client))

    def test_create_package(self):
        result = self.mock_client.create_package()
        self.assertIsInstance(result, Package)

    def test_create_release(self):
        result = self.mock_client.create_release()
        self.assertIsInstance(result, Release)

    def test_get_info(self):
        result = self.mock_client.get_info('foo')
        self.assertIsInstance(result, dict)

    def test_get_releases(self):
        result = self.mock_client.get_releases()
        self.assertIsInstance(result, str)
        d = json.loads(result)
        self.assertIn('releases', d)

    def test_get_stats(self):
        result = self.mock_client.get_stats()
        self.assertIsInstance(result, str)

    def test_package_start(self):
        self.assertEqual(self.mock_client.package_start(), True)

    def test_package_stop(self):
        self.assertEqual(self.mock_client.package_stop(), True)

    def test_ping(self):
        self.assertEqual(self.mock_client.ping(), True)

    def test_release_stop(self):
        self.assertEqual(self.mock_client.release_stop('foo'), True)

    def test_get_release(self):
        result = self.mock_client.get_release(str(uuid.uuid4()))
        self.assertIsInstance(result, Release)

    def test_deploy_release(self):
        result = self.mock_client.deploy_release(str(uuid.uuid4()))
        self.assertIs(result, True)

    def test_get_versions(self):
        result = self.mock_client.get_versions()
        self.assertIsInstance(result, dict)
