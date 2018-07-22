class ConsoleLogger:
    def __init__(self, bot):
        self.bot = bot
        self.session = set()

    async def on_open(self, sock):
        print(" [CL] Bot is ready")
        print(f" [CL] Connected on {sock.getpeername()}")

    async def on_data(self, ctx):
        print(f" [CL] > {ctx.message.raw}")

    async def on_raw(self, raw):
        print(f" [CL] < {raw}")

    async def on_error(self, e):
        print(f" ! Exception {repr(e)}")


def setup(bot):
    bot.add_cog(ConsoleLogger(bot))
