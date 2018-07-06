from discord.ext import commands
from .settings import Config

# Declare default cogs
default_modules = {
    "cogs.test",
    "cogs.db_logger"
}


class Bot(commands.Bot):
    def __init__(self):
        # Initialize Parent class
        super().__init__(command_prefix="으낙봇 ")

        # Get token from setting
        self.config = Config()
        self.token = self.config.get("Bot.Token")

        # Default cogs
        for name in default_modules:
            try:
                self.load_extension(name)
            except Exception as e:
                print(f"Failed to load extension: {name}.")
                raise e

    async def on_message(self, msg):
        print("""{0.server} {0.channel} {0.author} {0.content} {0.attachments} {0.embeds}""".format(msg))
        if msg.author.bot:
            return
        await self.process_commands(msg)

    def start_bot(self):
        self.run(self.token, bot=True)
