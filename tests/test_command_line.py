import unittest
import uuid
import orloclient
from test_mock import MockOrloClient
from mock import patch
import logging

"""
Testing the command line interface

This also serves as an example of how to use the mock class
"""

logging.basicConfig(level=logging.DEBUG)


@patch('orloclient.__main__.OrloClient', MockOrloClient)
class TestCommandLine(unittest.TestCase):
    def setUp(self):
        self.client = MockOrloClient('http://localhost')

        class Args:
            release = self.client.example_release.id
            package = self.client.example_package.id
            user = 'bob'
            platforms=['gumtree']
            team='adtech'
            references=['GTEPICS-FOO']
            name='my_name'
            version='1.0.0'
            note='blah blah'

        self.args = Args

    """
    These just test that the functions run, they are not good unit tests
    """

    def test_action_get_release(self):
        orloclient.__main__.action_get_release(self.client, self.args)

    def test_action_get_package(self):
        orloclient.__main__.action_get_package(self.client, self.args)

    def test_action_create_release(self):
        orloclient.__main__.action_create_release(self.client, self.args)

    def test_action_create_package(self):
        orloclient.__main__.action_create_package(self.client, self.args)

    def test_action_start(self):
        orloclient.__main__.action_start(self.client, self.args)

    def test_action_stop(self):
        orloclient.__main__.action_stop(self.client, self.args)
