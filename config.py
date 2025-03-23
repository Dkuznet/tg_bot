from decouple import config

API_ID: int = config("API_ID", cast=int)
API_HASH: str = config("API_HASH", cast=str)  # type: ignore
PHONE: str = config("PHONE", cast=str)  # type: ignore
BOT_TOKEN: str = config("BOT_TOKEN", cast=str)  # type: ignore

CHANNEL_ID: int = config("CHANNEL_ID", cast=int)
CHANNELS_FILENAME: str = config("CHANNELS_FILENAME", cast=str)  # type: ignore

SESSION: str = config("SESSION", cast=str)  # type: ignore
SYSTEM_VERSION: str = config("SYSTEM_VERSION", cast=str)  # type: ignore
DEVICE_MODEL: str = config("DEVICE_MODEL", cast=str)  # type: ignore
LANG_CODE: str = config("LANG_CODE", cast=str)  # type: ignore
SYSTEM_LANG_CODE: str = config("SYSTEM_LANG_CODE", cast=str)  # type: ignore
