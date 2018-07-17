import inspect
import asyncio


# Forked from discord.ext.commands.command
def command(name=None, cls=None, **attrs):
    if cls is None:
        cls = Command

    def decorator(func):
        if isinstance(func, Command):
            raise TypeError('Callback is already a command.')
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Callback must be a coroutine.')

        fname = name or func.__name__
        return cls(name=fname, callback=func, **attrs)

    return decorator


class Command:
    def __init__(self, name, callback, **attrs):
        self.name = name
        self.callback = callback
        self.aliases = attrs.get('aliases', [])
        self.pass_context = attrs.get('pass_context', False)


class Channel:
    def __init__(self, cid=""):
        self.name = cid


class User:
    def __init__(self, **kwargs):
        self.name = kwargs.get("uid", "")
        self.nick = kwargs.get("nick", self.name)
        self.tid = kwargs.get("tid", "")


class Message:
    def __init__(self, **kwargs):
        self.type = kwargs.get("type")
        self.channel = kwargs.get("channel")
        self.user = kwargs.get("user")
        self.raw = kwargs.get("raw", b"")
        self.message = kwargs.get("message", self.raw.decode())


class Context:
    def __init__(self, bot, channel: Channel, user: User, msg: Message):
        self.bot = bot
        self.channel = channel
        self.user = user
        self.message = msg

    async def reply(self, data):
        await self.bot.send_msg(self.channel, data)