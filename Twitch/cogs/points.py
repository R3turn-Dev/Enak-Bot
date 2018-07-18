from ..Enak.prototypes import command
from ..Enak.settings import Config
from ..Enak.db import PostgreSQL


class PointModule:
    def __init__(self, bot):
        self.bot = bot
        self.session = set()

        self.points = Config("./sub/points.ini").get("Twitch")
        self.db_config = Config("./sub/settings.ini")

        self.db = PostgreSQL(**self.db_config.get("PostgreSQL"))

    @command(['point', 'points'], pass_context=True)
    async def check_point_eng(self, ctx, *_):
        data = "_temp"
        await ctx.reply(f"@{ctx.user.name} Your Point: {data}p")

    @command(['포인트'], pass_context=True)
    async def check_point_kor(self, ctx, *_):
        data = "_temp"
        await ctx.reply(f"@{ctx.user.name} 당신의 포인트: {data}p")

    async def on_chat(self, ctx):
        _user = ctx.user
