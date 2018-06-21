from discord import Client, Game, Embed
from discord.ext import commands
from .db import PostgreSQL
from .settings import SettingManager
from json import dumps
from time import strftime, time
from asyncio import sleep

conf = SettingManager().get().PostgreSQL
DB = PostgreSQL(**conf)

BotConf = dict(DB.get_configuration())


default_modules = {
    "cogs.tests"
}

class Bot(commands.Bot):
    def __init__(self):
        # Initialize Parent class
        super().__init__(command_prefix="으낙아 ")

        # Get token from setting
        self.token = SettingManager().get().Token
        self.logger = DB.writeLog

        self.react_emoji = "👌"

        # Handler for DB Functions
        self.getCommands = DB.getCommands
        self.getChannelInfo = DB.getChannelInfo
        self.getFeedbackChannel = DB.getFeedbackChannel
        self.getTemplateMessage = DB.getTemplateMessage
        self.getAdmins = DB.getAdminInfo
        self.getFooter = DB.getFooter

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

