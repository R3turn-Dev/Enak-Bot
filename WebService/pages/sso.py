from engine import SingleWebPage
from settings import Config

from flask import render_template_string, send_from_directory, request
from flask_cors import cross_origin
from os.path import realpath
from time import time
from hashlib import sha256

encrypt = lambda x: sha256(x.encode()).hexdigest().upper()


class SSO:
    def __init__(self, engine, path="./pages/sso"):
        self.engine = engine

        self.parent = SingleWebPage(
            name="/sso",
            url_prefix="/sso",
            description="SSO (OAuth2소셜로그인)",
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

        @self.parent.bp.route('/twitch/')
        @cross_origin(["http://enakbot.return0927.xyz", "http://sso.return0927.xyz"])
        def twitch(*args, **kwargs):
            if request.args.get("access_token"):
                return render_template("ok.html")
            else:
                return render_template("index.html")

        @self.parent.bp.route("/discord/")
        @cross_origin(["http://enakbot.return0927.xyz", "http://sso.return0927.xyz"])
        def discord(*args, **kwargs):
            if "sso.return0927.xyz" in request.url:
                return render_template("index.html")

            token = request.args.get("code")
            if token:
                return render_template("ok.html")
            else:
                return "."

        @self.parent.bp.route("/<any(css, img, js, media):folder>/<path:filename>")
        def statics(folder, filename):
            return send_raw(folder, filename)

    def is_debugging(self):
        return self.engine.app.debug

def setup(engine):
    engine.register_blueprint(SSO(engine).parent.bp)