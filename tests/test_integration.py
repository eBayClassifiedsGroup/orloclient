from __future__ import print_function
from flask.ext.testing import LiveServerTestCase
from orloclient import Orlo
import orlo
import uuid

__author__ = 'alforbes'


class OrloLiveServerTest(LiveServerTestCase):
    """
    Test the Orlo client against the Orlo server

    When this gets more complex it will make sense to create a mock
    """

    def create_app(self):
        app = orlo.app
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.config['TRAP_HTTP_EXCEPTIONS'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['LIVESERVER_PORT'] = 7767
        # app.config['DEBUG'] = True

        orlo.orm.db.create_all()

        return orlo.app

    def setUp(self):
        self.orlo_client = Orlo(
            uri='http://localhost:7767'
        )

    def tearDown(self):
        orlo.orm.db.session.remove()
        orlo.orm.db.drop_all()

    def _create_release(self):
        return self.orlo_client.create_release('testuser', 'testplatform')

    def _create_package(self, release_id):
        return self.orlo_client.create_package(release_id, 'testName', '1.2.3')

    def _package_start(self, release_id, package_id):
        return self.orlo_client.package_start(release_id, package_id)

    def _package_stop(self, release_id, package_id, success=True):
        return self.orlo_client.package_stop(release_id, package_id, success)

    def _release_stop(self, release_id):
        return self.orlo_client.release_stop(release_id)


class OrloWriteTest(OrloLiveServerTest):
    """
    Test the write functions
    """

    def test_ping(self):
        """
        Test the orlo server actually runs
        """
        result = self.orlo_client.ping()
        self.assertIs(result, True)

    def test_create_release(self):
        """
        Create a release
        """
        result = self._create_release()

        self.assertIsInstance(result, uuid.UUID)

    def test_create_package(self):
        """
        Create package
        """
        release_id = self._create_release()
        result = self._create_package(release_id)

        self.assertIsInstance(result, uuid.UUID)

    def test_package_start(self):
        """
        Start a package
        """
        release_id = self._create_release()
        package_id = self._create_package(release_id)
        result = self._package_start(release_id, package_id)

        self.assertTrue(result)

    def test_package_stop(self):
        """
        Stop a package
        """
        release_id = self._create_release()
        package_id = self._create_package(release_id)
        self._package_start(release_id, package_id)
        result = self._package_stop(release_id, package_id)

        self.assertTrue(result)

    def test_release_stop(self):
        """
        Stop a release
        """
        release_id = self._create_release()
        result = self._release_stop(release_id)

        self.assertTrue(result)


class OrloReadTest(OrloLiveServerTest):
    """
    Test the read functions
    """

    def _setup_release(self):
        self.release_id = self._create_release()
        self.package_id = self._create_package(self.release_id)
        self._package_start(self.release_id, self.package_id)
        self._package_stop(self.release_id, self.package_id)
        self._release_stop(self.release_id)

    def test_get_releases(self):
        """
        Test that get_releases returns successfully without a filter
        """

        self._setup_release()
        result = self.orlo_client.get_releases()
        self.assertIsInstance(result, dict)

    def test_get_releases_package_name(self):
        """
        Test get_releases with a filter on package_name
        """

        self._setup_release()
        result = self.orlo_client.get_releases(package_name='testName')
        self.assertIsInstance(result, dict)

    def test_get_releases_user(self):
        """
        Test get_releases with a filter on user
        """
        self._setup_release()
        result = self.orlo_client.get_releases(user='testuser')
        self.assertIsInstance(result, dict)

    def test_get_releases_empty(self):
        """
        Test it doesn't blow up when filters don't match
        """
        result = self.orlo_client.get_releases()
        self.assertIsInstance(result, dict)
        self.assertEqual(0, len(result['releases']))

    def test_get_releases_empty_filter(self):
        """
        Test it doesn't blow up when filters don't match
        """
        result = self.orlo_client.get_releases(user='doesNotExist')
        self.assertIsInstance(result, dict)
        self.assertEqual(0, len(result['releases']))
