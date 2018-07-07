import socket
import asyncio


class TwichClient:
    def __init__(self, *args, **kwargs):
        self.host = kwargs.get("host")
        self.port = kwargs.get("port", 80)
        self.user = kwargs.get("user")
        self.token = kwargs.get("token")
        self.channel = kwargs.get("channel")

        self.on_open = kwargs.get("on_open", None)
        self.on_close = kwargs.get("on_close", None)
        self.on_error = kwargs.get("on_error", None)
        self.on_data = kwargs.get("on_data", None)

        self.socket = None
        self.loop = asyncio.get_event_loop()
        self.keep_running = False

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

    async def _callback(self, callback, *args):
        if callback:
            try:
                callback(*args)
            except Exception as e:
                raise Exception(f"Error on handing a callback {callback.name} / {e}")
                
    async def _run(self, *args, **kwargs):
        await self._connect(*args, **kwargs)
        await self._callback(self.on_open, self.socket)

        self.socket.send("PASS oauth:{}\n".format(self.token).encode())
        self.socket.send("NICK {}\n".format(self.user).encode())

        while self.keep_running:
            try:
                temp = self.socket.recv(1024)
                await self._callback(self.on_data, temp)

            except Exception as e:
                await self._callback(self.on_error, e)

        await self._callback(self.on_close)

    def run(self, *args, **kwargs):
        self.keep_running = True
        self.loop.run_until_complete(self._run())

    def close(self):
        self.socket.close()

