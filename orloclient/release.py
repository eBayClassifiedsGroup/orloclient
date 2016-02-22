from __future__ import print_function
from .exceptions import OrloClientError

__author__ = 'alforbes'


class OrloRelease(object):
    def __init__(self, release_id, user, platforms,
                 team=None,
                 references=None,
                 metadata=None,
                 note=None):
        """
        An Orlo Release

        :param UUID release_id:
        :param string user:
        :param list platforms:
        :param string team:
        :param list references:
        :param dict metadata:
        :param string note:
        :return:
        """

        self.release_id = release_id
        self.user = user
        self.platforms = platforms
        self.team = team
        self.references = references
        self.metadata = metadata
        self.note = note
        self.packages = []

    def deploy(self):
        raise NotImplementedError("Coming soon")
