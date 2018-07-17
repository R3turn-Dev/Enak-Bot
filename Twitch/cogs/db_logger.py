from Enak.db import PostgreSQL
from Enak.settings import Config
from Enak.prototypes import command


class DBLogger:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

    def _load_database(self):
        _config = Config().get("PostgreSQL")
        self.DB = PostgreSQL(**_config)

    async def write_log(self, event: str, **kwargs):
        self.DB.execute(f"INSERT INTO ")
