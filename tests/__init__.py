from unittest import TestCase
import uuid
from orloclient import OrloClient
from orloclient import Release, Package
from orloclient.mock_orlo import MockOrloClient


class OrloClientTest(TestCase):
    """
    Parent method for Orlo client tests

    Constants in this class are test parameters for Orlo methods
    """
    NOTE = 'test note'
    PLATFORMS = ['test_platform']
    REFERENCES = ['test_reference']
    TEAM = 'test_team'
    URI = 'http://localhost:1337'
    USER = 'test_user'

    CLIENT = MockOrloClient('http://dummy.example.com')
    RELEASE = Release(CLIENT, str(uuid.uuid4()))

    PACKAGE = RELEASE.packages[0]

    def setUp(self):
        self.orlo = OrloClient(self.URI)

