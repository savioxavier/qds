from collections.abc import Callable
from typing import Any, TypedDict


class MagicArguments(TypedDict):
    name: str
    type: Any
    desc: str


class MagicResponse(TypedDict):
    name: str
    desc: str
    args: list[MagicArguments]
    callable: Callable


def magic(fn: Callable) -> MagicResponse:
    args = getattr(fn, "_args", [])

    def _callable(*call_args, **call_kwargs):
        return fn(*call_args, **call_kwargs)

    return {
        "args": [{"name": arg[0], "type": arg[1], "desc": arg[2]} for arg in args],
        "callable": _callable,
    }
