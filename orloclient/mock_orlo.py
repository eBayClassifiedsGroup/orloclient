from __future__ import print_function
from orloclient import OrloClient
import json
import uuid

__author__ = 'alforbes'

"""
A very simple Mock Orlo object for testing in deployment scripts
"""


class MockOrloClient(object):
    """
    A mock Orlo Client

    Will return values from the example objects below.
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
        "user": "testuser",
        "metadata": {"env": "test", "pool": "web"}
    }

    example_stats = {
        "global": {
            "releases": {
                "normal": {
                    "failed": 1,
                    "successful": 10
                },
                "rollback": {
                    "failed": 1,
                    "successful": 2
                },
                "total": {
                    "failed": 2,
                    "successful": 12
                }
            }
        }
    }

    def __init__(self, uri, verify_ssl=True):
        self.uri = uri
        self.verify_ssl = verify_ssl

    def ping(self):
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

    def get_info(self, field, name=None, platform=None):
        return {'foo': {'bar': 1}}

    def get_stats(self, field=None, name=None, platform=None, stime=None, ftime=None):
        return json.dumps(self.example_stats)

    def release_stop(self, release_id):
        return True

    @staticmethod
    def package_start(*args, **kwargs):
        return True

    @staticmethod
    def package_stop(*args, **kwargs):
        return True
