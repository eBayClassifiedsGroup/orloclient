from __future__ import print_function
from flask.ext.testing import LiveServerTestCase
from orloclient import OrloClient, Release, Package
import orlo


__author__ = 'alforbes'


class OrloLiveServerTest(LiveServerTestCase):
    """
    Test the Orlo client against the Orlo server

    This is testing integration with the Orlo server, for tests that limit the scope to
    the client code see test_orloclient.py
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
        self.orlo_client = OrloClient(
            uri='http://localhost:7767'
        )

    def tearDown(self):
        orlo.orm.db.session.remove()
        orlo.orm.db.drop_all()

    def _create_release(self):
        return self.orlo_client.create_release('testuser', ['testplatform'])

    def _create_package(self, release):
        return self.orlo_client.create_package(release, 'testName', '1.2.3')

    def _package_start(self, package):
        return self.orlo_client.package_start(package)

    def _package_stop(self, package, success=True):
        return self.orlo_client.package_stop(package, success)

    def _release_stop(self, release):
        return self.orlo_client.release_stop(release)


class TestOrloWrite(OrloLiveServerTest):
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
        release = self._create_release()
        self.assertIsInstance(release, Release)

    def test_create_package(self):
        """
        Create package
        """
        release = self._create_release()
        result = self._create_package(release)
        self.assertIsInstance(result, Package)

    def test_package_start(self):
        """
        Start a package
        """
        release = self._create_release()
        package = self._create_package(release)
        result = self._package_start(package)

        self.assertTrue(result)

    def test_package_stop(self):
        """
        Stop a package
        """
        release = self._create_release()
        package = self._create_package(release)
        self._package_start(package)
        result = self._package_stop(package)

        self.assertTrue(result)

    def test_release_stop(self):
        """
        Stop a release
        """
        release = self._create_release()
        result = self._release_stop(release)
        self.assertTrue(result)


class TestOrloRead(OrloLiveServerTest):
    """
    Test the read functions
    """

    def _setup_release(self):
        """
        Setup a complete release to test against
        """
        self.release = self._create_release()
        self.package = self._create_package(self.release)
        self._package_start(self.package)
        self._package_stop(self.package)
        self._release_stop(self.release)

    def test_get_releases_package_name(self):
        """
        Test get_releases with a filter on package_name
        """
        self._setup_release()
        releases = self.orlo_client.get_releases(package_name='testName')
        self.assertIsInstance(releases[0], Release)

    def test_get_releases_user(self):
        """
        Test get_releases with a filter on user
        """
        self._setup_release()
        releases = self.orlo_client.get_releases(user='testuser')
        self.assertIsInstance(releases[0], Release)

    def test_get_releases_empty(self):
        """
        Test it doesn't blow up when there are no releases
        """
        releases = self.orlo_client.get_releases(user='blah_blah')
        self.assertIsInstance(releases, list)
        self.assertEqual(0, len(releases))

    def test_get_releases_empty_filter(self):
        """
        Test it doesn't blow up when filters don't match
        """
        self._create_release()
        releases = self.orlo_client.get_releases(user='doesNotExist')
        self.assertIsInstance(releases, list)
        self.assertEqual(0, len(releases))

