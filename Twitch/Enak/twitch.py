import socket
import asyncio
import inspect


class Command:
    def __init__(self, name):
        self.name = name

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
    callbacks : dict
        Callbacks to handle events
    cogs : dict
        Extensions for post upgrade
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
        self.channel = kwargs.get("channel")

        self.callbacks = {
            "on_open": [kwargs.get("on_open", None)],
            "on_close": [kwargs.get("on_close", None)],
            "on_error": [kwargs.get("on_error", None)],
            "on_data": [kwargs.get("on_data", None)]
        }

        self.cogs = {}
        self.commands = {}

        self.socket = None
        self.loop = asyncio.get_event_loop()
        self.keep_running = False

    def add_command(self, command):
        """Register a command :class:`Command` into TwitchBot.

        Parameters
        -----------------
        command
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
        if not isinstance(command, Command):
            raise TypeError("This object was not defined as a subclass of Command")

        for name in command.name:
            if name in self.commands.keys():
                raise Exception(f"Command {name} was already registered")

            self.commands[name] = command


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
                        callback(*args)
            except Exception as e:
                raise Exception(f"Error on handing a callback {callback.name} / {e}")
                
    async def _run(self, *args, **kwargs):
        await self._connect(*args, **kwargs)
        await self._callback(self.callbacks['on_open'], self.socket)

        self.socket.send("PASS oauth:{}\n".format(self.token).encode())
        self.socket.send("NICK {}\n".format(self.user).encode())

        while self.keep_running:
            try:
                temp = self.socket.recv(1024)
                await self._callback(self.callbacks['on_data'], temp)

            except Exception as e:
                await self._callback(self.callbacks['on_error'], e)

        await self._callback(self.callbacks['on_close'])

    def run(self, *args, **kwargs):
        self.keep_running = True
        self.loop.run_until_complete(self._run())

    def close(self):
        self.socket.close()

