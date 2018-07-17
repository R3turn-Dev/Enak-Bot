from Enak.db import PostgreSQL
from Enak.settings import Config


class CustomCommands:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

        self.config = Config("./sub/settings.ini")
        # self.db = PostgreSQL(**self.config.get("PostgreSQL"))

    async def on_ready(self, *args, **kwargs):
        print(f" Activated {__file__}")


def setup(bot):
    bot.add_cog(CustomCommands(bot))