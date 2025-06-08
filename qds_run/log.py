import sys
import traceback

from rich.console import Console

from .symbols import BAR_CHAR

console = Console()
rprint = console.print


def formatted_print(text: str):
    for line in text.split("\n"):
        console.print(f"    [dim green]{BAR_CHAR}[/dim green] {line}", highlight=False)


class QdsLogger:
    def __init__(self):
        pass

    def error(self, *messages: str):
        for message in messages:
            if isinstance(message, Exception):
                traceback.print_exception(message)

            rprint(f"\\[qds-error] [red]{message}[/red]")

        sys.exit()

    def success(self, *messages: str):
        rprint(f"\\[qds-info] [green]{' '.join(messages)}[/green]")
