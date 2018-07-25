from settings import Config
from engine import FlaskEngine


config = Config()

engine = FlaskEngine(
    config.get("Web"),
    webpages=[
        "pages.root",
        "pages.login",
        "pages.sso"
    ]
)

engine.run()