from __future__ import print_function
from .exceptions import OrloClientError

__author__ = 'alforbes'


class OrloRelease(object):
    def __init__(self, client, release_id=None, create=False, **kwargs):
        """
        An Orlo Release

        :param client: Instance of orloclient.Orlo
        :param release_id:
        :return:
        """
        if not release_id and not create:
            raise OrloClientError("Must specify a release_id, or create must be True")

        self.client = client
        self.release_id = release_id
        self.kwargs = kwargs

    def create(self):
        """
        Create this release on the server
        """
        rid = self.client.create_release(
            user=self.kwargs.get('user'),
            platforms=self.kwargs.get('platforms'),
            team=self.kwargs.get('team'),
            references=self.kwargs.get('references'),
            note=self.kwargs.get('references'),
        )
        return rid

    def get(self):
        """
        Fetch this release from the server
        :return:
        """
        release = self.client.get_releases(release_id=self.release_id)
        print(release)
