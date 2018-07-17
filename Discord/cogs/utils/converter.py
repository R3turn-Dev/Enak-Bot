from Enak.db import PostgreSQL
from Enak.settings import SettingManager


conf = SettingManager().get().PostgreSQL
DB = PostgreSQL(**conf)


_FORMAT = """
from discord.ext import commands
from random import choice


class {server_ident}:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

{commands}

def setup(bot):
    bot.add_cog({server_ident}(bot))
"""

_COMMAND_FORMAT = """
    @commands.command('{command.present}', pass_context=True)
    async def {command.global}(self, ctx, *args, **kwargs):
        stack = {
            "ㅎㅇㅎㅇ",
            "으낙입니다",
            "그러는 당신은?"
        ]

        await self.bot.send_message(ctx.message.channel, choice(stack))
"""
