from discord.ext import commands
from json import dumps
from Enak.db import PostgreSQL
from Enak.settings import Config


class Logger:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

        self.config = Config("./sub/settings.ini")
        self.db = PostgreSQL(**self.config.get("PostgreSQL"))

    async def event_log(self, **kwargs):
        cur = self.db._get_cursor()

        e_type = kwargs.get("type")
        server =  kwargs.get("server")
        channel =  kwargs.get("channel")
        user =  kwargs.get("user")
        lore =  kwargs.get("lore")

        cur.execute(
            f"INSERT INTO events (type, server, channel, user, lore)"
            f"VALUES ('{e_type}', '{server}', '{channel}', '{user}', E'{lore}');"
        )

    async def msg_log(self, msg):
        server_id = "0" if msg.server is None else msg.server.id
        channel_id = msg.channel.id
        author_id = msg.author.id
        content = msg.content
        attachments = dumps(msg.attachments)
        embeds = dumps(msg.embeds)

        cur = self.db._get_cursor()

        cur.execute(
            f"INSERT INTO messages (msg_id, server, channel, author, content, attachments, embeds)"
            f" VALUES ({msg.id}, '{server_id}', '{channel_id}', '{author_id}', "
            f"E'{content}', E'{attachments}', E'{embeds}');"
        )

    async def on_ready(self, *args, **kwargs):
        print(" Activated cogs.db_logger")

    async def on_message(self, msg):
        await self.msg_log(msg)

def setup(bot):
    bot.add_cog(Logger(bot))