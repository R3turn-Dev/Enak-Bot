from json import dumps
from re import escape
from threading import get_ident

from psycopg2 import connect


class PostgreSQL:
    def __init__(self, initial_connect=True, **kwargs):
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 5432)
        self.user = kwargs.get("user", "postgres")
        self.pw = kwargs.get("password", "")
        self.db = kwargs.get("database", "postgres")

        self.conn = None
        self.cursor = None

        self.connDict = {}
        self.curDict = {}

        self.escaper = escape

        if initial_connect:
            self.getConn()
            self.getCursor()

    def getConn(self):
        self.conn = connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pw,
            database=self.db
        )

        self.conn.autocommit = True
        return self.conn

    def getCursor(self):
        thread_id = get_ident().__int__()

        if thread_id not in self.connDict.keys():
            self.connDict[thread_id] = self.getConn()

        if thread_id not in self.curDict.keys():
            self.curDict[thread_id] = self.connDict[thread_id].cursor()

        return self.curDict[thread_id]

    def execute(self, query):
        cur = self.getCursor()
        cur.execute(query)
        return cur

    def add_user(self, platform, **kwargs):
        _logged_in = kwargs.get("now")
        if platform == "discord":
            uid = kwargs.get("uid")
            email = kwargs.get("email")
            name = kwargs.get("name")

            _already_registered = self.execute(f"SELECT uuid FROM users WHERE discord='{uid}';").fetchall()

            if _already_registered:
                print("Already registered as ", _already_registered[0][0])
                return [False, _already_registered[0][0]]

            if not self.execute(f"SELECT did FROM discord WHERE did='{uid}';").fetchall():
                self.execute(f"INSERT INTO discord (did, email, username) VALUES ('{uid}', '{email}', '{name}') RETURNING did;").fetchall()

            if _logged_in:
                _uuid = _logged_in
                _uuid = self.execute(f"UPDATE users SET discord='{uid}' WHERE uuid='{_uuid}' RETURNING uuid;").fetchall()
                print("Added new platform into ", _uuid[0][0])
            else:
                _uuid = self.execute(f"INSERT INTO users (discord) VALUES ('{uid}') RETURNING uuid;").fetchall()
                print("New user registered as ", _uuid[0][0])

            return [True, _uuid[0][0]]

        elif platform == "twitch":
            tid = kwargs.get("tid")
            uid = kwargs.get("uid")
            email = kwargs.get("email")
            name = kwargs.get("name")

            _already_registered = self.execute(f"SELECT uuid FROM users WHERE twitch='{tid}';").fetchall()

            if _already_registered:
                print("Already registered as ", _already_registered[0][0])
                return [False, _already_registered[0][0]]

            if not self.execute(f"SELECT tid FROM twitch WHERE tid='{tid}';").fetchall():
                self.execute(f"INSERT INTO twitch (tid, uid, email, username) VALUES ('{tid}', '{uid}', '{email}', '{name}') RETURNING tid;").fetchall()
                
            if _logged_in:
                _uuid = _logged_in
                _uuid = self.execute(f"UPDATE users SET twitch='{tid}' WHERE uuid='{_uuid}' RETURNING uuid;").fetchall()
                print("Added new platform into ", _uuid[0][0])
            else:
                _uuid = self.execute(f"INSERT INTO users (twitch) VALUES ('{tid}') RETURNING uuid;").fetchall()
                print("New user registered as ", _uuid[0][0])

            return [True, _uuid[0][0]]
