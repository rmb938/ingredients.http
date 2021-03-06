import pytest
import webtest

from ingredients_http.app import HTTPApplication
from ingredients_http.app_mount import ApplicationMount
from ingredients_http.test.base import LOGGING_CONFIG


class TWebApplication(HTTPApplication):
    pass


class TMountBad(ApplicationMount):
    def __init__(self, app: HTTPApplication):
        super().__init__(app=app, mount_point='/', routers_location='bad')


class TMountNoRoutes(ApplicationMount):
    def __init__(self, app: HTTPApplication):
        super().__init__(app=app, mount_point='/', routers_location='routes.none')


class TMountWithRoutes(ApplicationMount):
    def __init__(self, app: HTTPApplication):
        super().__init__(app=app, mount_point='/', routers_location='routes.with')


class TestWebApplication(object):
    def test_no_mounts(self):
        app = TWebApplication(logging_config=LOGGING_CONFIG)
        app.setup()

    def test_mount_bad_route_location(self):
        app = TWebApplication(logging_config=LOGGING_CONFIG)

        app.register_mount(TMountBad(app))

        with pytest.raises(ImportError):
            app.setup()

    def test_mount_no_routes(self):
        app = TWebApplication(logging_config=LOGGING_CONFIG)

        app.register_mount(TMountNoRoutes(app))
        app.setup()

        test_app = webtest.TestApp(app.wsgi_application)
        test_app.get("/", status=404)

    def test_mount_with_routes(self):
        app = TWebApplication(logging_config=LOGGING_CONFIG)

        app.register_mount(TMountWithRoutes(app))
        app.setup()

        test_app = webtest.TestApp(app.wsgi_application)
        test_app.get("/foo")
        resp = test_app.post_json('/foo', {"foo": "bar"})
        assert resp.json == {"foo": "bar"}
