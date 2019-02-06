from abc import ABCMeta, abstractmethod

import pytest
from webtest import TestApp


class APITestCase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def app_cls(self):
        raise NotImplementedError

    @abstractmethod
    def setup_mounts(self, app):
        pass

    @pytest.yield_fixture()
    def app(self):
        app = self.app_cls()()
        self.setup_mounts(app)

        app.setup()

        yield app

    @pytest.yield_fixture()
    def wsgi(self, app):
        yield TestApp(app.wsgi_application)
