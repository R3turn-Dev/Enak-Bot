from engine import SingleWebPage
from db import PostgreSQL
from settings import Config

from flask import render_template_string, send_from_directory, request, session, redirect
from os.path import realpath
from time import time
from hashlib import sha256

encrypt = lambda x: sha256(x.encode()).hexdigest().upper()


class Service:
    def __init__(self, engine, path="./pages/rank"):
        self.engine = engine

        self.db = PostgreSQL(**Config().get("AppDatabase"))
        self.web_db = PostgreSQL(**Config().get("Database"))

        self.parent = SingleWebPage(
            name="/ranks",
            url_prefix="/ranks",
            description="Rank (랭킹)",
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

        @self.parent.bp.route("/")
        def root(*args, **kwargs):
            return """<script>location.href='/';</script>"""

        @self.parent.bp.route('/<path:channel>')
        def ranks(channel, **kwargs):
            channels = [*{*[x[0] for x in self.db.execute("SELECT channel FROM points;").fetchall()]}]
            if not channel in channels:
                return """<script>alert('올바르지 않은 채널명입니다.');location.href='/';</script>"""

            sel = request.args.get("view", "")
            if sel == "my":
                _logged_in_platforms = session.get("li_platform")
                if not (_logged_in_platforms and "twitch" in _logged_in_platforms):
                    return redirect(f"/login/?redirect={request.url}")

                # return repr(session['uuid'])
                tid = self.web_db.execute(f"SELECT twitch FROM users WHERE uuid='{session['uuid']}';").fetchall()[0][0]
                uid = self.web_db.execute(f"SELECT uid FROM twitch WHERE tid='{tid}';").fetchall()[0][0]
                data = self.db.execute(f"SELECT channel, point FROM points WHERE \"user\"='{uid}' ORDER BY channel DESC;").fetchall()

                _out = []
                for c, p in data:
                    _channel_data = self.db.execute(f"SELECT \"user\", point, RANK() OVER(ORDER BY point DESC) FROM points WHERE channel='{c}' ORDER BY point DESC;").fetchall()
                    _out.append([c, p, [u for u, _, _ in _channel_data].index(uid)])
                
                return render_template(
                    "my.html",
                    debugstring=f"?{time()}" if self.is_debugging() else "",
                    session=session,
                    user=_logged_in_platforms['twitch']['name'],
                    channel=channel,
                    data=_out
                )

            elif sel == "":
                data = self.db.execute(f"SELECT \"user\", point, RANK() OVER(ORDER BY point DESC) FROM points WHERE channel='{channel}' ORDER BY point DESC;").fetchall()

                if session.get("li_platform") and "twitch" in session.get("li_platform"):
                    tid = self.web_db.execute(f"SELECT twitch FROM users WHERE uuid='{session['uuid']}';").fetchall()[0][0]
                    uid = self.web_db.execute(f"SELECT uid FROM twitch WHERE tid='{tid}';").fetchall()[0][0]

                    data = [[u[:2]+("*"*(len(u)-2)), v, r, u == uid] for u, v, r in data]
                    data.sort(key=lambda x:x[3])
                    me = data[-1]
                    data = [me] + data[:-1]
                else:
                    data = [[u[:2]+("*"*(len(u)-2)), v, r, False] for u, v, r in data]
                p = [p for u, p, r, me in data]
                top_5 = sum(p[:5])/sum(p)*100
                top_10 = sum(p[:10])/sum(p)*100
                
                return render_template(
                    "index.html",
                    debugstring=f"?{time()}" if self.is_debugging() else "",
                    session=session,
                    channel=channel,
                    data=data[:100],
                    perc_10=top_10,
                    perc_5=top_5,
                    sel=sel
                )

            else:
                return """<script>alert('없는 페이지입니다.');history.go(-1);</script>"""

        @self.parent.bp.route("/<any(css, img, js, media):folder>/<path:filename>")
        def statics(folder, filename):
            return send_raw(folder, filename)

    def is_debugging(self):
        return self.engine.app.debug

def setup(engine):
    engine.register_blueprint(Service(engine).parent.bp)