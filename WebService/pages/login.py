from engine import SingleWebPage
from settings import Config

from flask import render_template_string, send_from_directory
from os.path import realpath
from time import time
from hashlib import sha256

encrypt = lambda x: sha256(x.encode()).hexdigest().upper()


class Login:
    def __init__(self, engine, path="./pages/login"):
        self.uris = Config().get("SSO")

        self.engine = engine

        self.parent = SingleWebPage(
            name="/login",
            url_prefix="/login",
            description="Login (로그인페이지)",
            template_folder=path
        )
        self.mobile_platform = ['android', 'iphone', 'blackberry']

        def render_template(template_name, **kwargs):
            return render_template_string(
                open(f"{realpath(self.parent.bp.template_folder)}/{template_name}", "r", encoding="UTF-8").read(),
                **kwargs
            )

        def send_raw(folder, fname):
            return send_from_directory(f"{realpath(self.parent.bp.template_folder)}", f"{folder}/{fname}")

        @self.parent.bp.route('/')
        def root(*args, **kwargs):
            return render_template(
                "index.html",
                debugstring=f"?{time()}" if self.is_debugging() else "",
                **self.uris
            )

        @self.parent.bp.route("/<any(css, img, js, media):folder>/<path:filename>")
        def statics(folder, filename):
            return send_raw(folder, filename)

    def is_debugging(self):
        return self.engine.app.debug

def setup(engine):
    engine.register_blueprint(Login(engine).parent.bp)