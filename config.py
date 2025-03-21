from decouple import config

API_ID: int = config("API_ID", cast=int)
API_HASH: str = config("API_HASH", cast=str)  # type: ignore
PHONE: str = config("PHONE", cast=str)  # type: ignore
BOT_TOKEN: str = config("BOT_TOKEN", cast=str)  # type: ignore
