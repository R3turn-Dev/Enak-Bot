from .twitch import TwichClient
from .settings import Config


default_cogs = [
    'cogs.console_logger'
]


class Bot(TwichClient):
    def __init__(self, *args, **kwargs):
        self.config = Config()
        self.user = kwargs.get("user", self.config.get("Bot.username"))
        self.cid = kwargs.get("token", self.config.get("Bot.Client-ID"))
        self.csc = kwargs.get("token", self.config.get("Bot.Client-Secret"))
        self.channels = kwargs.get("channels", [v.strip() for v in self.config.get("Bot.channels").split(",")])
        self._default_cogs = kwargs.get("cogs", default_cogs)

        kwargs['user'] = self.user
        kwargs['cid'] = self.cid
        kwargs['csc'] = self.csc
        kwargs['channels'] = self.channels

        super().__init__(*args, **kwargs)

        for cog in self._default_cogs:
            self.load_extension(cog)