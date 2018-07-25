from flask import Flask, Blueprint
from os import urandom

import importlib
import sys

from exceptions import NotValidModuleException


class FlaskEngine:
    def __init__(self, configuration, **kwargs):
        self.app = Flask(__name__)
        self.config = configuration

        self.modules = {}
        self.webpages = kwargs.get("webpages", [])

        for name in self.webpages:
            self.register_webpage(name)

    def register_blueprint(self, *args, **kwargs):
        self.app.register_blueprint(*args, **kwargs)

    def register_webpage(self, name: str):
        if name in self.app.blueprints:
            return

        lib = importlib.import_module(name)
        if not hasattr(lib, "setup"):
            del lib
            del sys.modules[name]

            raise NotValidModuleException(f"{name} has a setup function")

        lib.setup(self)
        self.modules[name] = lib

    def run(self, *args, **kwargs):
        conf = self.config.copy()
        secret_key = conf.get("secret_key", urandom(32))
        del conf['secret_key']

        for k, v in kwargs.items():
            conf[k] = v

        self.app.secret_key = secret_key
        self.app.run(*args, **conf)


class SingleWebPage:
    def __init__(self,  name=None, route_path=None, description=None, *args, **kwargs):
        self.name = name
        self.route_path = route_path
        self.description = description

        if "name" in kwargs.keys():
            self.name = kwargs['name']
            del kwargs['name']
        if "route_path" in kwargs.keys():
            self.route_path = kwargs['route_path']
            del kwargs['route_path']
        if "description" in kwargs.keys():
            self.description = kwargs['description']
            del kwargs['description']

        self.bp = Blueprint(name, __name__, *args, **kwargs)

    def extract(self):
        return self.bp
