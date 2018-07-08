from Enak import Bot

extensions = [
    "cogs.basic_commands"
]

client = Bot(
    host = "irc.twitch.tv",
    cogs = extensions
)
client.run()