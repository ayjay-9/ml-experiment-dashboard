from decouple import config

from .base import *  # noqa: F401,F403

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True
