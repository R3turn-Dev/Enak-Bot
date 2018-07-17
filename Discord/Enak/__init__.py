from discord.ext import commands
from .settings import Config

# Declare default cogs
default_modules = {
    "cogs.red_string",
    "cogs.console_logger"
}


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        # Initialize Parent class
        super().__init__(
            command_prefix=kwargs.get("command_prefix", kwargs.get("cpx", "\0"))
        )

        # Get token from setting
        self.config = Config()
        self.token = self.config.get("Bot.Token")

        # Default cogs
        cogs = kwargs.get("cogs", default_modules)

        for name in cogs:
            try:
                self.load_extension(name)
            except Exception as e:
                print(f"Failed to load extension: {name}.")
                raise e

    def start_bot(self):
        self.run(self.token, bot=True)
