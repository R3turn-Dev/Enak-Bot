from settings import Config
from engine import FlaskEngine


config = Config()

engine = FlaskEngine(
    config.get("Web"),
    webpages=[
        "pages.root",
        "pages.login",
        "pages.sso",
        "pages.service",
        "pages.profile",
        "pages.rank"
    ]
)

engine.run()