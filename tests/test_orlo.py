from __future__ import print_function
from flask.ext.testing import LiveServerTestCase
from orloclient import Orlo
import orlo
import uuid

__author__ = 'alforbes'


class OrloLiveServerTest(LiveServerTestCase):
    """
    Base class for tests which contains the methods required to move
    releases and packages through the workflow
    """

    def create_app(self):
        app = orlo.app
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.config['TRAP_HTTP_EXCEPTIONS'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['LIVESERVER_PORT'] = 7767
        app.config['USE_RELOADER'] = False

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
        return self.orlo_client.create_release('testuser', 'testteam', 'testplatform')

    def _create_package(self, release_id):
        return self.orlo_client.create_package(release_id, 'testName', '1.2.3')

    def _start_package(self, release_id, package_id):
        return self.orlo_client.start_package(release_id, package_id)

    def _stop_package(self, release_id, package_id, success=True):
        return self.orlo_client.stop_package(release_id, package_id, success)

    def _stop_release(self, release_id):
        return self.orlo_client.stop_release(release_id)

    def test_ping(self):
        """
        Test the orlo server actually runs

        :return:
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

    def test_start_package(self):
        """
        Start a package
        """
        release_id = self._create_release()
        package_id = self._create_package(release_id)
        result = self._start_package(release_id, package_id)

        self.assertTrue(result)

    def test_stop_package(self):
        """
        Stop a package
        """
        release_id = self._create_release()
        package_id = self._create_package(release_id)
        self._start_package(release_id, package_id)
        result = self._stop_package(release_id, package_id)

        self.assertTrue(result)

    def test_stop_release(self):
        """
        Stop a release
        """
        release_id = self._create_release()
        result = self._stop_release(release_id)

        self.assertTrue(result)
