from discord.ext import commands
from random import choice


class RandomFeedback:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

    @commands.command('안녕', pass_context=True)
    async def hello(self, ctx, *args, **kwargs):
        stack = [
            "ㅎㅇㅎㅇ",
            "으낙입니다",
            "그러는 당신은?"
        ]

        await self.bot.send_message(ctx.message.channel, choice(stack))


def setup(bot):
    bot.add_cog(RandomFeedback(bot))
