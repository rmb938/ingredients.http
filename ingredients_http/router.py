import inspect
import logging
from abc import ABCMeta
from typing import List, Callable

import cherrypy

from ingredients_http.request_methods import RequestMethods


class Router(object):
    __metaclass__ = ABCMeta

    def __init__(self, uri_base=None):
        self.logger = logging.getLogger("%s.%s" % (self.__module__, self.__class__.__name__))

        self.uri_base = uri_base
        self.mount = None

    def __register_route(self, dispatcher: cherrypy.dispatch.RoutesDispatcher, uri_prefix: str, route: str,
                         action: Callable,
                         methods: List[RequestMethods] = None):
        if methods is None:
            methods = [RequestMethods.GET]

        method_names = [rm.value for rm in methods]
        if uri_prefix == '/':
            complete_uri = uri_prefix + (self.uri_base if self.uri_base is not None else '')
        else:
            complete_uri = uri_prefix + ("/" + self.uri_base if self.uri_base is not None else '')

        complete_uri = complete_uri + ("/" + route if route else '')

        self.logger.debug(
            "Registering route " + complete_uri + " with action " + action.__name__ + " and allowed methods " + str(
                method_names))

        self.on_register(complete_uri, action, methods)
        dispatcher.connect(self.__module__ + "." + self.__class__.__name__ + "." + action.__name__,
                           complete_uri, controller=self, action=action.__name__, conditions=dict(method=method_names))

    def on_register(self, uri: str, action: Callable, methods: List[RequestMethods]):
        pass

    def setup_routes(self, dispatcher: cherrypy.dispatch.RoutesDispatcher, uri_prefix: str):

        for member in [getattr(self, attr) for attr in dir(self)]:
            if inspect.ismethod(member) and hasattr(member, '_route'):
                self.__register_route(dispatcher, uri_prefix, member._route, member, member._methods)
