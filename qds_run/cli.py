import datetime
import importlib
import os
from inspect import cleandoc
from typing import Annotated, Any, NewType, Optional
from rich.syntax import Syntax

from cyclopts import App, Parameter
from InquirerPy import inquirer
from pathlib import Path
from pyboxen import boxen

from .constants import QDS_DIR, QDS_INITIAL_CONTENTS, logger, qds_config
from .log import formatted_print, rprint
from .runner import magic
from .symbols import DOT_CHAR, RIGHT_CHEVRON

QdsUnknown = NewType("QdsUnknown", Any)

QDS_DIR.mkdir(parents=True, exist_ok=True)


def _rfc3339_to_humanized(rfc3339: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(rfc3339.replace("Z", "+00:00"))
        humanized = dt.strftime("%Y-%m-%d %H:%M:%S %Z%z")
        return humanized
    except ValueError:
        return "wrong RFC3339 format"


def _file_exists(filename: Path) -> bool:
    return filename.is_file()


def _as_qds_dir(filename: Path) -> Path:
    return QDS_DIR / filename


def _run_qds(name: str):
    filepath = str(_as_qds_dir(name + ".py"))

    fn_name = "run"

    module_name = filepath

    spec = importlib.util.spec_from_file_location(module_name, str(filepath))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fn_callable_entity = getattr(mod, fn_name)

    parsed = magic(fn_callable_entity)

    parsed_script_args = parsed["args"]
    parsed_script_callable = parsed["callable"]

    script_data = qds_config.get_script_data(name)
    script_desc = script_data.get("desc", "A qds script")

    print(
        boxen(
            script_desc,
            title=name,
            color="cyan",
            padding=1,
            margin=1,
        )
    )

    argument_list = {}

    for arg in parsed_script_args:
        arg_name = arg.get("name", "Argument name")
        arg_desc = arg.get("desc", "Argument description")

        rprint(
            f"[yellow]    {arg_name}[/yellow][dim] {DOT_CHAR} {arg_desc}[/dim]",
            highlight=False,
        )
        value = inquirer.text(
            "", qmark=f"    {RIGHT_CHEVRON}", amark=f"    {RIGHT_CHEVRON}"
        ).execute()

        print()
        argument_list.update({arg_name: value})

    exec_output = parsed_script_callable(**argument_list)

    output = exec_output
    if exec_output is None:
        output = "[dim][i]This script returned no output. Please ensure that the 'run' function returns a string[/]"

    rprint("    [cyan]Output[/cyan]\n")
    formatted_print(str(output))


def _add_qds(filename: Path, config: QdsUnknown, contents: Optional[str] = ""):
    if _file_exists(filename):
        raise FileExistsError

    try:
        qds_config.write(config)
    except Exception as e:
        logger.error("TODO: qds add error", e)

    with open(filename, "w") as f:
        f.write(contents)


def _delete_qds(name: str):
    filename = _as_qds_dir(name + ".py")

    if not _file_exists(filename):
        raise FileNotFoundError

    try:
        os.remove(filename)
        qds_config.delete(name)
    except Exception as e:
        logger.error("qds deletion error", e)


def _rename_qds(name: str, new_name: str):
    filename = _as_qds_dir(name + ".py")
    new_filename = _as_qds_dir(new_name + ".py")

    if not _file_exists(filename):
        raise FileNotFoundError

    try:
        os.rename(filename, new_filename)

        qds_config.rename(name, new_name)
    except Exception as e:
        logger.error("qds rename error", e)


def _update_qds(
    name: str,
    config: QdsUnknown,
):
    filename = _as_qds_dir(name + ".py")

    if not _file_exists(filename):
        raise FileNotFoundError

    try:
        qds_config.update(name, config)
    except Exception as e:
        logger.error("qds update error", e)


def _list_qds():
    contents = qds_config.load_config()
    if not contents:
        return

    scripts = contents.value

    formatted = ""

    rprint(f"[green]{len(scripts)} qds scripts found[/green]\n")

    for idx, (name, info) in enumerate(scripts.items()):
        formatted += cleandoc(
            f"""{idx + 1}. [cyan]{name}[/cyan]
            [dim]created at  [/dim][yellow]{_rfc3339_to_humanized(info.get("created_at", ""))}[/yellow]
            [dim]description [/dim]{info.get("desc", "")}
            """
        )
        formatted += "\n\n"

    return formatted.strip()


def _view_qds(name: str):
    filename = _as_qds_dir(name + ".py")

    if not _file_exists(filename):
        raise FileNotFoundError

    try:
        rprint(f"File {filename}\n")
        rprint(
            Syntax.from_path(
                filename,
                line_numbers=True,
                theme="github-dark",
                background_color="default",
            )
        )

    except Exception as e:
        logger.error("qds view error", e)


app = App()


@app.command
def add(
    name: Annotated[
        Optional[str],
        Parameter(
            ["--name", "-n"],
            required=False,
        ),
    ] = None,
    desc: Annotated[
        Optional[str],
        Parameter(
            ["--desc", "-d"],
            required=False,
        ),
    ] = None,
):
    """Add a new qds script

    Will be saved to ~/.qds/<name>.py

    Parameters
    ----------
    name
        The name of the qds script (optional, will trigger prompt if unspecified)
    desc
        The description of the qds script (optional, will trigger prompt if unspecified)
    """
    if not name:
        name = inquirer.text("What do you want to name this qds script?").execute()

    filename = _as_qds_dir(name + ".py")
    if _file_exists(filename):
        logger.error(f"The qds script '{name}' already exists. Try using another name")

    if not desc:
        desc = inquirer.text(
            f"Provide a short description for the '{name}' qds script:"
        ).execute()

    config = {
        "name": name,
        "desc": desc,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    try:
        _add_qds(
            filename=_as_qds_dir(filename),
            contents=QDS_INITIAL_CONTENTS,
            config=config,
        )
    except Exception as e:
        logger.error(e)

    logger.success(f"The qds script '{name}' has been sucessfully created")
    logger.success(
        f"Please check out '{_as_qds_dir(filename)}' to edit script configuration"
    )


@app.command
def list():
    """Lists all qds scripts"""

    string = _list_qds()

    if not string:
        logger.error("There are no qds scripts to display")
    else:
        rprint(string, highlight=False)


@app.command
def view(
    name: Annotated[
        Optional[str],
        Parameter(
            ["--name", "-n"],
            required=False,
        ),
    ] = None,
):
    """View a qds script

    Parameters
    ----------
    name
        The name of the qds script (optional, will trigger prompt if unspecified)
    """

    all_scripts = qds_config.list_all_scripts()

    if not all_scripts:
        logger.error("There are no qds scripts to view")

    if not name:
        name = inquirer.select(
            "Which qds script do you want to view?",
            choices=all_scripts,
        ).execute()

    if name not in all_scripts:
        logger.error(f"No such script '{name}' exists")

    try:
        _view_qds(name)
    except Exception as e:
        logger.error(e)


@app.command
def delete(
    name: Annotated[
        Optional[str],
        Parameter(
            ["--name", "-n"],
            required=False,
        ),
    ] = None,
):
    """Delete a qds script

    Parameters
    ----------
    name
        The name of the qds script (optional, will trigger prompt if unspecified)
    """
    all_scripts = qds_config.list_all_scripts()

    if not all_scripts:
        logger.error("There are no qds scripts to delete")

    if not name:
        name = inquirer.select(
            "Which qds script do you want to delete?",
            choices=all_scripts,
        ).execute()

    if name not in all_scripts:
        logger.error(f"No such script '{name}' exists")

    try:
        _delete_qds(name)
    except Exception as e:
        logger.error(e)

    logger.success(f"The qds script '{name}' has been sucessfully deleted")


@app.command
def rename(
    name: Annotated[
        Optional[str],
        Parameter(
            ["--name", "-n"],
            required=False,
        ),
    ] = None,
    new_name: Annotated[
        Optional[str],
        Parameter(
            ["--new-name", "-N"],
            required=False,
        ),
    ] = None,
):
    """Rename a qds script

    Parameters
    ----------
    name
        The current name of the qds script (optional, will trigger prompt if unspecified)
    new_name
        The new name of the qds script (optional, will trigger prompt if unspecified)
    """
    all_scripts = qds_config.list_all_scripts()

    if not all_scripts:
        logger.error("There are no qds scripts to rename")

    if not name:
        name = inquirer.select(
            "Which qds script do you want to rename?",
            choices=all_scripts,
        ).execute()

    if name not in all_scripts:
        logger.error(f"No such script '{name}' exists")

    if not new_name:
        new_name = inquirer.text(
            f"What do you want to rename the script '{name}' to?",
        ).execute()

    if name == new_name:
        logger.error("Both the old name and new name are the same")

    if new_name in all_scripts:
        logger.error(
            f"There already exists a script named script '{name}'. Please choose another one"
        )

    try:
        _rename_qds(name, new_name)
    except Exception as e:
        logger.error(e)

    logger.success(
        f"The qds script '{name}' has been sucessfully renamed to '{new_name}'"
    )


@app.command
def update(
    name: Annotated[
        Optional[str],
        Parameter(
            ["--name", "-n"],
            required=False,
        ),
    ] = None,
    desc: Annotated[
        Optional[str],
        Parameter(
            ["--desc", "-d"],
            required=False,
        ),
    ] = None,
):
    """Update the description of a qds script

    Parameters
    ----------
    name
        The name of the qds script (optional, will trigger prompt if unspecified)
    desc
        The description of the qds script (optional, will trigger prompt if unspecified)
    """
    all_scripts = qds_config.list_all_scripts()

    if not all_scripts:
        logger.error("There are no qds scripts to update")

    if not name:
        name = inquirer.select(
            "Which qds script do you want to update?",
            choices=all_scripts,
        ).execute()

    if name not in all_scripts:
        logger.error(f"No such script '{name}' exists")

    if not desc:
        desc = inquirer.text(
            f"What do you want to update the description of the script '{name}' to?",
        ).execute()

    try:
        _update_qds(name, {"desc": desc})
    except Exception as e:
        logger.error(e)

    logger.success(f"The qds script '{name}' has been sucessfully updated")


@app.command
def run(
    name: Annotated[
        Optional[str],
        Parameter(
            ["--name", "-n"],
            required=False,
        ),
    ] = None,
):
    """Delete a qds script

    Parameters
    ----------
    name
        The name of the qds script (optional, will trigger prompt if unspecified)
    """
    all_scripts = qds_config.list_all_scripts()

    if not all_scripts:
        logger.error("There are no qds scripts to run")

    if not name:
        name = inquirer.select(
            "Which qds script do you want to run?",
            choices=all_scripts,
        ).execute()

    if name not in all_scripts:
        logger.error(f"No such script '{name}' exists")

    try:
        _run_qds(name)
    except Exception as e:
        logger.error(e)


def main():
    app()


if __name__ == "__main__":
    main()
