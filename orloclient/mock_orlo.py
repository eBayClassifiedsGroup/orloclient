from __future__ import print_function
import json
import uuid

__author__ = 'alforbes'

"""
A very simple Mock Orlo object for testing
"""


class MockOrlo(object):
    """
    Reference object to our Orlo server
    """
    example_package = {
        "status": "SUCCESSFUL",
        "name": "testName",
        "version": "1.2.3",
        "ftime": "2015-11-27T11:32:34Z",
        "stime": "2015-11-27T11:32:34Z",
        "duration": 0,
        "diff_url": None,
        "id": str(uuid.uuid4())
    }

    example_release = {
        "platforms": [
            "testplatform"
        ],
        "ftime": "2015-11-27T11:32:34Z",
        "stime": "2015-11-27T11:32:34Z",
        "team": None,
        "duration": 0,
        "references": [],
        "packages": [example_package],
        "id": str(uuid.uuid4()),
        "user": "testuser"
    }

    def __init__(self, uri, requests_verify=True):
        self.uri = uri
        self.requests_verify = requests_verify

    @staticmethod
    def ping():
        return True

    def get_releases(self, *args, **kwargs):
        response = {
            'releases': [self.example_release]
        }
        return json.dumps(response)

    def create_release(self, *args, **kwargs):
        return uuid.UUID(self.example_release['id'])

    def create_package(self, *args, **kwargs):
        return uuid.UUID(self.example_package['id'])

    @staticmethod
    def release_stop(release_id):
        return True

    @staticmethod
    def package_start(*args, **kwargs):
        return True

    @staticmethod
    def package_stop(*args, **kwargs):
        return True
