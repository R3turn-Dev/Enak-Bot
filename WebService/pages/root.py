from engine import SingleWebPage
from flask import render_template, send_from_directory
from time import time
from hashlib import sha256

encrypt = lambda x: sha256(x.encode()).hexdigest().upper()


class Root:
    def __init__(self, engine, path="./pages/root"):
        self.engine = engine

        self.parent = SingleWebPage(
            name="/",
            url_prefix="",
            description="Root 홈(메인페이지)",
            template_folder=path
        )
        self.mobile_platform = ['android', 'iphone', 'blackberry']

        @self.parent.bp.route('/')
        def root(*args, **kwargs):
            return render_template(
                "index.html",
                debugstring=f"?{time()}" if self.is_debugging() else ""
            )

        @self.parent.bp.route("/discord")
        def discord(*args, **kwargs):
            return render_template(
                "discord.html",
                debugstring=f"?{time()}" if self.is_debugging() else ""
            )

        @self.parent.bp.route("/<any(css, img, js, media):folder>/<path:filename>")
        def statics(folder, filename):
            return send_from_directory(f"{path}/{self.parent.name}/", f"{folder}/{filename}")

    def is_debugging(self):
        return self.engine.app.debug

def setup(engine):
    engine.register_blueprint(Root(engine).parent.bp)