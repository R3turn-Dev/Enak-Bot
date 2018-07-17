import sys


class ConsoleOutput:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

    async def on_ready(self, *args, **kwargs):
        print(f" Activated {__file__}")

    async def on_message(self, msg):
        print(msg.id, msg.server, msg.channel, msg.author, msg.content)


def setup(bot):
    bot.add_cog(ConsoleOutput(bot))