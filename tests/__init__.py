from unittest import TestCase
import uuid
from orloclient import OrloClient


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
        self.orlo = OrloClient(self.URI)

