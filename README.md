# qds

`qds` (Quick Dirty Scripts) is a CLI tool that lets you create and run quick Python scripts from the command line with minimal setup.

## Installation

Install via pip:

```bash
pip install qds-run
```

## Overview

When you first run any `qds` command, it initializes a directory in your home folder:

- **`~/.qds/qds.toml`**
  A TOML file containing metadata about your scripts.

- **`~/.qds/<script>.py`**
  Python files where each script’s code lives.

You can then add, edit, list, rename, run, and delete these scripts directly from your terminal.

## Basic Usage

1. **Initialize your workspace**
   The first time you invoke any command, `~/.qds/qds.toml` and the `~/.qds/` folder will be created automatically.

2. **Create a new script skeleton**

   ```bash
   qds add <script_name>
   ```

   For example:

   ```bash
   qds add base64conv
   ```

   You’ll be prompted to enter a description; after confirming, a file named `~/.qds/base64conv.py` is created.

3. **Edit your script**
   Open `~/.qds/base64conv.py` in your editor. By default, it will contain a template like this:

   ```python
   from qds import qds

   @qds(
       args=[("text", str, "Sample text to be provided")],
   )
   def run(text: str) -> str:
       pass
   ```

   - **`@qds` decorator**

     - `args`: a list of `(name, type, description)` tuples defining the arguments your script accepts.

   - **`run` function**

     - The entry point; return a string to be printed.

4. **Run your script**

   You will be prompted to fill in the arguments.

   ```bash
   qds run base64conv
   ```

## Example: Text to Base64 Converter

1. Add the script:

   ```bash
   qds add base64conv
   ```

2. Edit `~/.qds/base64conv.py` so that `run` looks like this:

   ```python
   import base64
   from qds import qds

   @qds(
       args=[("text", str, "Text to encode to Base64")],
   )
   def run(text: str) -> str:
       encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
       return encoded
   ```

3. Use it:

   ```bash
   $ qds run base64
   ```

## Available Commands

| Command         | Description                           |
| --------------- | ------------------------------------- |
| `qds add`       | Create a new script skeleton          |
| `qds delete`    | Delete an existing script             |
| `qds list`      | List all available scripts            |
| `qds rename`    | Rename a script                       |
| `qds run`       | Run a script with the given arguments |
| `qds update`    | Update the description of a script    |
| `qds view`      | Show the source code of a script      |
| `qds --help`    | Display help message                  |
| `qds --version` | Display application version           |
