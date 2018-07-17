from Enak import Bot

extensions = [
    "cogs.basic_commands",
    "cogs.console_logger"
]

client = Bot(
    host="irc.twitch.tv",
    port=6667,
    command_prefix="!",
    cogs=extensions
)
client.run()
