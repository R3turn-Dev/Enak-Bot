from engine import SingleWebPage
from settings import Config
from db import PostgreSQL

from requests import get
from aiohttp import ClientSession
from flask import render_template_string, send_from_directory, request, session
from flask_cors import cross_origin
from os.path import realpath
from time import time
from hashlib import sha256

encrypt = lambda x: sha256(x.encode()).hexdigest().upper()


class SSO:
    def __init__(self, engine, path="./pages/sso"):
        self.engine = engine
        self.db = PostgreSQL(**Config().get("Database"))

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
                google_analystics=open(f"{realpath(self.parent.bp.template_folder)}/../global/gtag.html", "r", encoding="UTF-8").read(),
                **kwargs
            )

        def send_raw(folder, fname):
            return send_from_directory(f"{realpath(self.parent.bp.template_folder)}", f"{folder}/{fname}")

        @self.parent.bp.route('/twitch/')
        @cross_origin(["http://enakbot.return0927.xyz", "http://sso.return0927.xyz"])
        def twitch(*args, **kwargs):
            token = request.args.get("access_token")
            if token:
                resp = get("https://api.twitch.tv/kraken/user", headers={
                    "Accept": "application/vnd.twitchtv.v5+json",
                    "Client-ID": Config().get("Cresentials")['twitch-cid'],
                    "Authorization": f"OAuth {token}"
                }).json()

                _name = resp['display_name']
                _uid = resp['name']
                _tid = resp['_id']
                _email = resp.get('email')

                _first_join, _uuid = self.db.add_user("twitch", email=_email, name=_name, uid=_uid, tid=_tid, now=session.get("uuid"))
                session['uuid'] = _uuid
                
                if not isinstance(session.get('li_platform'), dict):
                    session['li_platform'] = {}
                session['li_platform']['twitch'] = {
                    "name": _name
                }

                return render_template("ok.html")
            else:
                return render_template("index.html")

        @self.parent.bp.route("/discord/")
        @cross_origin(["http://enakbot.return0927.xyz", "http://sso.return0927.xyz"])
        def discord(*args, **kwargs):
            if "sso.return0927.xyz" in request.url:
                return render_template("index.html")

            token = request.args.get("access_token")
            if token:
                resp = get("https://discordapp.com/api/users/@me",headers={"Authorization": f"Bearer {token}"}).json()
                _email = resp['email']
                _name = resp['username']
                _id = resp['id']

                _first_join, _uuid = self.db.add_user("discord", email=_email, name=_name, uid=_id, now=session.get("uuid"))
                session['uuid'] = _uuid
                
                if not isinstance(session.get('li_platform'), dict):
                    session['li_platform'] = {}
                session['li_platform']['discord'] = {
                    "name": _name
                }

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