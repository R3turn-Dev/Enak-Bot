from Enak import TwichClient
from Enak.settings import Config

def handler(*args):
    print(args)

def message(b_msg):
    print(b_msg.decode())

config = Config()
name = config.get("Credentials.username")
token = config.get("Credentials.OAuth_token")

print(
    f"""
    Accessing Twitch IRC

    [ Credentials ]
    User  : {name}
    Token : {token[:5]}*******************************
    """
)

client = TwichClient(host="irc.twitch.tv", name = name, token = token, on_open = handler, on_close = handler, on_data = message)
client.run()