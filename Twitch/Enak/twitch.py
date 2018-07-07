import re
import sys
import socket
import asyncio
import inspect
import importlib

from .prototypes import Channel, User, Message, ctx
from discord.ext.commands import Command, command


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

    """

    def __init__(self, *args, **kwargs):
        self.host = kwargs.get("host")
        self.port = kwargs.get("port", 80)
        self.user = kwargs.get("user")
        self.token = kwargs.get("token")
        self.channels = kwargs.get("channels", [])

        self.command_prefix = kwargs.get("command_prefix", "!")

        self.callbacks = {
            "on_open": [kwargs.get("on_open", None)],
            "on_close": [kwargs.get("on_close", None)],
            "on_error": [kwargs.get("on_error", None)],
            "on_joined": [kwargs.get("on_joined", None)],
            "on_data": [kwargs.get("on_data", None)]
        }

        self.cogs = {}
        self.extensions = {}
        self.commands = {}

        self.socket = None
        self.loop = asyncio.get_event_loop()
        self.keep_running = False

        self.re = re.compile("^(PING)|:(.*)!.*PRIVMSG #(.*) :(.*)$")

    async def process_command(self, data):
        msg = data.decode()

        if msg.startswith(self.command_prefix):
            name, *args = msg[1:].split(" ")

            if name in self.commands:
                command = self.commands[name]

                if command.pass_context:
                    await command(ctx, args)
                else:
                    await command(args)

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
        name = func.__name__ if name is None else name

        if not asyncio.iscoroutinefunction(func):
            raise Exception("Listener must be coroutines")

        if name in self.callbacks.keys():
            self.callbacks[name].append(func)
        else:
            self.callbacks[name] = [func]

    def add_cog(self, cog):
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
            self.socket.send(f"PRIVMSG #{channel.name} {data}\n".encode())
        elif isinstance(channel, str):
            self.socket.send(f"PRIVMSG #{channel} {data}\n".encode())
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
                raise Exception(f"Error on handing a callback {callback.name} / {e}")

    async def _join_channel(self, channel):
        if self.socket and not self.socket._closed:
            try:
                self.socket.send(f"JOIN #{channel}\n".encode())
            except Exception as e:
                raise Exception(f"Error occured when joining channel / {repr(e)}")
        else:
            raise Exception(f"Error occured when joining channel / {repr(e)}")
                
    async def _run(self, *args, **kwargs):
        await self._connect(*args, **kwargs)
        await self._callback(self.callbacks['on_open'], self.socket)

        self.socket.send("PASS oauth:{}\n".format(self.token).encode())
        self.socket.send("NICK {}\n".format(self.user).encode())

        for channel in self.channels:
            await self._join_channel(channel)

        while self.keep_running:
            try:
                data = self.socket.recv(1024)
                [glob, user, channel, msg] = self.re.findall(data)[0]

                if glob == "PING":
                    self.socket.send(b"PING :tmi.twitch.tv\n")

                else:
                    temp = ctx(
                        self,
                        Channel(channel),
                        User(user),
                            Message(
                            type = "message",
                            channel = Channel(channel),
                            user = User(user),
                            message = msg
                        )
                    )

                await self._callback(self.callbacks['on_data'], temp)

            except Exception as e:
                await self._callback(self.callbacks['on_error'], e)

        await self._callback(self.callbacks['on_close'])

    def run(self, *args, **kwargs):
        self.keep_running = True
        self.loop.run_until_complete(self._run())

    def close(self):
        self.socket.close()

