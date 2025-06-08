import functools
from collections.abc import Callable
from typing import Any


def qds(
    args: list[tuple[Any]],
):
    def builder(func: Callable):
        @functools.wraps(func)
        def executor(*args, **kwargs):
            result = func(*args, **kwargs)

            return result

        executor._args = args
        return executor

    return builder
