from os import environ
from typing import Any

from dotenv import load_dotenv as core_load_dotenv

load_dotenv = core_load_dotenv


def get(key: str) -> Any | None:
    return environ.get(key)


def get_bool(key: str) -> bool | None:
    val = environ.get(key)

    if val is None:
        return None

    if val.lower() == "false":
        return False
    if val.lower() == "true":
        return True

    raise ValueError(f"The key value for {key} must be eiter true or false")
