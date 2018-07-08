# Examples


## Discord Bot

### Settings.ini
```ini
[Bot]
Token = ZWIv11XyFQvg2ITiGvhWYSFR.EJhx13.0zotpzw5exxweN-PsqfPmk6ftpe

[PostgreSQL]
host = 0.0.0.0
port = 5432
user = enak-bot
password = This_Is_Super_Password
database = Enak-Bot
```

### Example Bot
```py
from Enak import Bot as DiscordBot

Bot = DiscordBot()
Bot.start_bot()
```

### Example Cogs
- Parse Youtube Information when command "홍연"
```py
import aiohttp
import asyncio
from discord.ext import commands


class RedString:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

    @commands.command("홍연", pass_context=True)
    async def red(self, ctx):
        async with aiohttp.ClientSession() as sess:
            async with sess.get("https://content.googleapis.com/youtube/v3/videos?part=contentDetails%2Cstatistics&id=f9bY6pVIUW8&key=lemzTC4TuPDyCIVVwDKduPzffgaSesCECoT1Rg6") as resp:
                data = await resp.json()
                temp = data['items'][0]['statistics']

                view = temp['viewCount']
                like = temp['likeCount']
                disl = temp['dislikeCount']
                comment = temp['commentCount']

                await self.bot.send_message(ctx.message.channel, f"View\t\t\t\t{view}\nLikes\t\t\t\t{like} : {disl}\tDislikes\nComment\t\t{comment}")


def setup(bot):
    bot.add_cog(RedString(bot))
```
- Save Messages into Database
```py
from discord.ext import commands
from json import dumps
from Enak.db import PostgreSQL
from Enak.settings import Config


class Logger:
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

        self.config = Config("./sub/settings.ini")
        self.db = PostgreSQL(**self.config.get("PostgreSQL"))

    async def event_log(self, **kwargs):
        cur = self.db._get_cursor()

        e_type = kwargs.get("type")
        server =  kwargs.get("server")
        channel =  kwargs.get("channel")
        user =  kwargs.get("user")
        lore =  kwargs.get("lore")

        cur.execute(
            f"INSERT INTO events (type, server, channel, user, lore)"
            f"VALUES ('{e_type}', '{server}', '{channel}', '{user}', E'{lore}');"
        )

    async def msg_log(self, msg):
        server_id = "0" if msg.server is None else msg.server.id
        channel_id = msg.channel.id
        author_id = msg.author.id
        content = msg.content
        attachments = dumps(msg.attachments)
        embeds = dumps(msg.embeds)

        cur = self.db._get_cursor()

        cur.execute(
            f"INSERT INTO messages (msg_id, server, channel, author, content, attachments, embeds)"
            f" VALUES ({msg.id}, '{server_id}', '{channel_id}', '{author_id}', "
            f"E'{content}', E'{attachments}', E'{embeds}');"
        )

    async def on_ready(self, *args, **kwargs):
        print(" Activated cogs.db_logger")

    async def on_message(self, msg):
        await self.msg_log(msg)

def setup(bot):
    bot.add_cog(Logger(bot))
```


## Twitch Bot

### Settings.ini
```ini
[Bot]
username = EnakBot
Client-Id = JcRsRrC4uprBxLkinAjffuTyMgD0Ys
Client-Secret = mWnbCHhEIsiacgcpZ7xxg3p3swGAQN
Channels = return0927, enak-bot, habomm
```

### Example Bot
```py
from Enak import Bot as TwitchBot

client = TwitchBot(
    host="irc.twitch.tv"
)
client.run()
```

### Example Cogs
- Process 'uptime' command
```py
from Enak.prototypes import command


class BasicCommands:
    def __init__(self, bot):
        self.bot = bot
        self.session = set()


    @command(['uptime', '업타임'])
    async def uptime(self, ctx, *, data):
        await ctx.reply("Yes")

def setup(bot):
    print("I was activated")
    bot.add_cog(BasicCommands(bot))
```

- Log data on console
```py
class ConsoleLogger:
    def __init__(self, bot):
        self.bot = bot
        self.session = set()

    async def on_data(self, data):
        print(data.decode())

def setup(bot):
    bot.add_cog(ConsoleLogger(bot))
```