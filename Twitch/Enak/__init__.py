from .twitch import TwichClient
from .settings import Config


default_cogs = [
    'cogs.basic_commands',
    'cogs.console_logger'
]


class Bot(TwichClient):
    def __init__(self, *args, **kwargs):
        self.config = Config()
        print(self.config.get("Bot.username"))
        print(self.config.get("Bot.OAuth_token"))
        print(self.config.get("Bot.channels"))
        self.user = kwargs.get("user", self.config.get("Bot.username"))
        self.token = kwargs.get("token", self.config.get("Bot.OAuth_token"))
        self.channels = kwargs.get("channels", [v.strip() for v in self.config.get("Bot.channels").split(",")])

        kwargs['user'] = self.user
        kwargs['token'] = self.token
        kwargs['channels'] = self.channels

        super().__init__(*args, **kwargs)

        for cog in default_cogs:
            self.load_extension(cog)