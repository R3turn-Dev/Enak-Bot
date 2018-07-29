from psycopg2 import connect
from threading import get_ident


class PostgreSQL:
    def __init__(self, initial_connect=True, **kwargs):
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 5432)
        self.user = kwargs.get("user", "postgres")
        self.pw = kwargs.get("password", "")
        self.db = kwargs.get("database", "EnakBot")

        self.conn = None
        self.cursor = None

        self.connDict = {}
        self.curDict = {}

        if initial_connect:
            self.get_connection()
            self.get_cursor()

    def get_connection(self):
        self.conn = connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pw,
            database=self.db
        )

        self.conn.autocommit = True
        return self.conn

    def get_cursor(self):
        thread_id = get_ident().__int__()

        if thread_id not in self.connDict.keys():
            self.connDict[thread_id] = self.get_connection()

        if thread_id not in self.curDict.keys():
            self.curDict[thread_id] = self.connDict[thread_id].cursor()

        return self.curDict[thread_id]

    def execute(self, query):
        cur = self.get_cursor()
        cur.execute(query)
        return cur

