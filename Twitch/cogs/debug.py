class Debugger:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

    async def on_error(self, e):
        print(f"""Error: {repr(e)}
        Data: {e.data}""")

    async def on_data(self, raw):
        if raw.message.type in ["PING"]:
            print(f"""PING : {raw.message.raw}""")


def setup(bot):
    bot.add_cog(Debugger(bot))
