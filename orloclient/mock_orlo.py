from __future__ import print_function
from orloclient import OrloClient, Release, Package
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
    example_package_dict = {
        "status": "SUCCESSFUL",
        "name": "testName",
        "version": "1.2.3",
        "ftime": "2015-11-27T11:32:34Z",
        "stime": "2015-11-27T11:32:34Z",
        "duration": 0,
        "diff_url": None,
        "id": str(uuid.uuid4())
    }

    example_release_dict = {
        "platforms": [
            "testplatform"
        ],
        "ftime": "2015-11-27T11:32:34Z",
        "stime": "2015-11-27T11:32:34Z",
        "team": None,
        "duration": 0,
        "references": [],
        "packages": [example_package_dict],
        "id": str(uuid.uuid4()),
        "user": "testuser",
        "metadata": {"env": "test", "pool": "web"}
    }

    example_stats_dict = {
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

        self.example_release = Release(
            self, self.example_release_dict['id']
        )

        self.example_package = Package(
            self.example_release_dict['id'],
            self.example_package_dict['id'],
            self.example_package_dict['name'],
            self.example_package_dict['version'],
        )

    def ping(self):
        return True

    def get_release(self, release_id):
        return Release(self, release_id)

    def get_release_json(self, release_id):
        return {
            'releases': [self.example_release_dict]
        }

    def get_releases(self, *args, **kwargs):
        response = {
            'releases': [self.example_release_dict]
        }
        return json.dumps(response)

    def create_release(self, *args, **kwargs):
        return self.example_release

    def create_package(self, *args, **kwargs):
        return self.example_package

    @staticmethod
    def get_info(field, name=None, platform=None):
        return {'foo': {'bar': 1}}

    def get_stats(self, field=None, name=None, platform=None, stime=None, ftime=None):
        return json.dumps(self.example_stats_dict)

    @staticmethod
    def release_stop(release_id):
        return True

    @staticmethod
    def package_start(*args, **kwargs):
        return True

    @staticmethod
    def package_stop(*args, **kwargs):
        return True

    @staticmethod
    def deploy_release(*args, **kwargs):
        return True

    @staticmethod
    def get_versions():
        return {'package_one': '1.2.3'}
