import re
import sys
import socket
import aiohttp
import asyncio
import inspect
import importlib
from datetime import datetime, timedelta

from .prototypes import Channel, User, Message, Context, Command, command


class APIConnector:
    def __init__(self, cid, csc):
        self.client_id = cid
        self.csc = csc

    def _make_header(self):
        return {
            'Accept': "application/vnd.twitchtv.v5+json",
            'Client-ID': self.client_id,
            'Authorization': f"OAuth {self.csc}"
        }

    async def get_user_by_name(self, name):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://api.twitch.tv/kraken/users?login={name}", headers=self._make_header()) as resp:
                data = await resp.json()

                _temp = data['users'][0]
                _nick = _temp['display_name']
                _tid = _temp['_id']

                return User(uid=name, nick=_nick, tid=_tid)

    async def get_user_by_id(self, uid):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://api.twitch.tv/kraken/users/{uid}", headers=self._make_header()) as resp:
                data = await resp.json()

                _nick = data['display_name']
                _name = data['name']

                return User(uid=_name, nick=_nick, tid=uid)

    async def get_stream(self, uid):
        if not uid:
            return None

        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://api.twitch.tv/kraken/streams/{uid}", headers=self._make_header()) as resp:
                data = await resp.json()

                _stream = data['stream']

                if _stream is None:
                    return None

                _title = _stream['channel']['status']
                _game = _stream['game']
                _viewer = _stream['viewers']
                _created_at = datetime.strptime(_stream['created_at'], "%Y-%m-%dT%H:%M:%SZ")

                return {"title": _title, "game": _game, "viewers": _viewer, "createdAt": _created_at}

    async def get_uptime(self, uid):
        _data = await self.get_stream(uid)

        if _data:
            _start = _data['createdAt']
            return self.humanizeTimeDiff(_start)
        else:
            return "방송중이 아닙니다."

    def humanizeTimeDiff(self, timestamp = timedelta(seconds=0)):
        """
        Returns a humanized string representing time difference
        between now() and the input timestamp.

        The output rounds up to days, hours, minutes, or seconds.
        4 days 5 hours returns '4 days'
        0 days 4 hours 3 minutes returns '4 hours', etc...
        """

        timeDiff = datetime.utcnow() - timestamp
        days = timeDiff.days
        hours = timeDiff.seconds/3600
        minutes = timeDiff.seconds%3600/60
        seconds = timeDiff.seconds%3600%60

        out = []
        tStr = ""
        if days > 0:
            if days == 1:   tStr = "day"
            else:           tStr = "days"
            out.append("%d %s" %(days, tStr))
        if hours > 0:
            if hours == 1:  tStr = "hour"
            else:           tStr = "hours"
            out.append("%d %s" %(hours, tStr))
        if minutes > 0:
            if minutes == 1:tStr = "min"
            else:           tStr = "mins"
            out.append("%d %s" %(minutes, tStr))
        if seconds > 0:
            if seconds == 1:tStr = "sec"
            else:           tStr = "secs"
            out.append("%d %s" %(seconds, tStr))
        return ", ".join(out)

class TwichClient:
    """Simple Command-Based Twitch Chatbot Client.

    Attributes
    -------------
    host : str
        Server URI to connect
    port : int
        Server port to connect
    user : str
        Twitch User ID to act as
    token : str
        Twitch OAuth2 Token to login with
    channel : list
        Twitch Channels to join
    command_prefix : str
        Command prefix for command identifying
    callbacks : dict
        Callbacks to handle events
    cogs : dict
        Extensions for post upgrade
    extensions: dict
        Extensions containing cogs
    commands : dict
        Commands to process in Twitch Chatting
    socket : socket.socket
        Socket to contact with server
    loop
        Main loop of a bot
    keep_running : bool
    re : _sre.SRE_PATTERN
        A re expression to parse a message
    """

    def __init__(self, *args, **kwargs):
        self.host = kwargs.get("host")
        self.port = kwargs.get("port", 80)
        self.user = kwargs.get("user")
        self.cid = kwargs.get("cid")
        self.csc = kwargs.get("csc")
        self.channels = kwargs.get("channels", [])
        self._users = {}

        self.APIHandler = APIConnector(self.cid, self.csc)

        self.command_prefix = kwargs.get("command_prefix", "!")

        self.callbacks = {
            "on_open": [kwargs.get("on_open", None)],
            "on_close": [kwargs.get("on_close", None)],
            "on_error": [kwargs.get("on_error", None)],
            "on_joined": [kwargs.get("on_joined", None)],
            "on_data": [kwargs.get("on_data", None)],
            "on_chat": [kwargs.get("on_chat", None)]
        }

        self.cogs = {}
        self.extensions = {}
        self.commands = {}

        self.socket = None
        self.loop = asyncio.get_event_loop()
        self.keep_running = False

        self.re = re.compile(r"^(PING)|:(.*)!.*(JOIN) #(.*)$|:(.*)!.*(PRIVMSG) #(.*) :(.*)$|^:(|.*)tmi.twitch.tv (\d\d\d) (.*) :(.*)$")

    async def _build_user_info(self, name):
        if not name in self._users:
            self._user = await self.APIHandler.get_user_by_name(name)

    async def get_user_info(self, name):
        if name in self._users:
            return self._users[name]
        else:
            await self._build_user_info(name)
            return User(uid=name)

    async def process_command(self, ctx):
        """Determine a message is issued for command and process a cog

        Parameters
        -----------------
        ctx : Enak.prototypes.Context
            A context containing information of chat data

        Raises
        ---------
        None

        Returns
        ---------
        None
        """
        msg = ctx.message.message

        if msg.startswith(self.command_prefix):
            name, *args = msg[1:].split(" ")

            if name in self.commands:
                _command = self.commands[name]

                if _command.pass_context:
                    await _command.callback(None, ctx, args)
                else:
                    await _command.callback(None, args)

    def add_command(self, cmd):
        """Register a command :class:`Command` into TwitchBot.

        Parameters
        -----------------
        cmd
            The command to add.

        Raises
        ---------
        Exception
            If the command is already registered
        TypeError
            If the passed command is not a subclass of :class:`Command`.

        Returns
        ---------
        None
        """
        if not isinstance(cmd, Command):
            raise TypeError("This object was not defined as a subclass of Command")

        for name in cmd.name:
            if name in self.commands.keys():
                raise Exception(f"Command {name} was already registered")

            self.commands[name] = cmd


    def add_listener(self, func, name=None):
        """Register a listener event :class:`function`

        Parameters
        -----------------
        func
            The corutine function to process an event.
        name
            A specific name of function

        Raises
        ---------
        Exception
            If the command is not a coroutine functinon.

        Returns
        ---------
        None
        """
        name = func.__name__ if name is None else name

        if not asyncio.iscoroutinefunction(func):
            raise Exception("Listener must be coroutines")

        if name in self.callbacks.keys():
            self.callbacks[name].append(func)
        else:
            self.callbacks[name] = [func]

    def add_cog(self, cog):
        """Register a cog containing commands :class:`function` and events :class:`function`

        Parameters
        -----------------
        cog
            A class containing commands and events

        Raises
        ---------
        None

        Returns
        ---------
        None
        """
        self.cogs[type(cog).__name__] = cog

        members = inspect.getmembers(cog)
        for name, member in members:
            if isinstance(member, Command):
                self.add_command(member)
            
            if name.startswith('on_'):
                self.add_listener(member)

    def load_extension(self, name):
        if name in self.extensions:
            return

        lib = importlib.import_module(name)
        if not hasattr(lib, 'setup'):
            del lib
            del sys.modules[name]

            raise Exception("This module has not to setup.")

        lib.setup(self)
        self.extensions[name] = lib

    async def send_msg(self, channel, data: str):
        if isinstance(channel, Channel):
            self.socket.send(f"PRIVMSG #{channel.name} :{data}\n".encode())
        elif isinstance(channel, str):
            self.socket.send(f"PRIVMSG #{channel} :{data}\n".encode())
        else:
            raise Exception("Channel passed is not supported type.")

    def _setup(self, conn=None, **kwargs):
        if conn:
            self.host, self.port, = conn
        elif kwargs:
            self.host = kwargs.get("host")
            self.port = kwargs.get("port", 80)

        self.socket = socket.socket()

    async def _connect(self, *args, **kwargs):
        self._setup(*args, **kwargs)
        self.socket.connect((self.host, self.port))

    async def _callback(self, callbacks: list, *args):
        if callbacks:
            try:
                for callback in callbacks:
                    if callback:
                        await callback(*args)
            except Exception as e:
                raise Exception(f"Error on handling a callback {callback} / {e}")

    async def _join_channel(self, channel):
        if self.socket and not self.socket._closed:
            try:
                self.socket.send(f"JOIN #{channel}\n".encode())
            except Exception as e:
                raise Exception(f"Error occured when joining channel / {repr(e)}")
        else:
            raise Exception(f"Error occured when joining channel / {repr(e)}")
                
    async def _run(self, *args, **kwargs):
        await self._build_user_info(self.user)
        await self._connect(*args, **kwargs)
        await self._callback(self.callbacks['on_open'], self.socket)

        self.socket.send(f"PASS oauth:{self.csc}\n".encode())
        self.socket.send(f"NICK {self.user}\n".encode())

        for channel in self.channels:
            await self._join_channel(channel)
            await self._build_user_info(channel)

        while self.keep_running:
            try:
                data = self.socket.recv(1024)

                for _data in data.decode().split("\r\n")[:-1]:
                    glob, _, _, _, _user, _type, _channel, _message, _me, _code, _self, _info = self.re.findall(_data)[0]

                    temp = Context(
                        self,
                        Channel(),
                        User(),
                        Message()
                    )

                    if _user: await self._build_user_info(_user)

                    if glob == "PING":
                        self.socket.send(b"PING :tmi.twitch.tv\n")

                        temp.channel.name = "GLOBAL"

                        temp.user.name = "SYSTEM"

                        temp.message.type = "PING"
                        temp.message.user = temp.user
                        temp.message.channle = temp.channel
                        temp.message.raw = _data

                    else:
                        temp.channel.name = _channel

                        temp.user.name = _user

                        temp.message.type = "chat"
                        temp.message.user = temp.user
                        temp.message.channel = temp.channel
                        temp.message.raw = _data
                        temp.message.message = _message

                    await self.process_command(temp)
                    await self._callback(self.callbacks['on_data'], temp)
                    if temp.message.type == "chat": await self._callback(self.callbacks['on_chat'], temp)

            except Exception as e:
                await self._callback(self.callbacks['on_error'], Exception(f" Error on internal {repr(e)}"))

        await self._callback(self.callbacks['on_close'])

    def run(self, *args, **kwargs):
        self.keep_running = True
        self.loop.run_until_complete(self._run())

    def close(self):
        self.socket.close()

