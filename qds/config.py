import os

import tomlkit


class QdsConfig:
    def __init__(self, config_path):
        self.config_path = config_path

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return tomlkit.loads(f.read())

        return tomlkit.document()

    def save_config(self, toml_doc):
        with open(self.config_path, "w") as f:
            f.write(tomlkit.dumps(toml_doc).strip())

    def write(self, qds_data: dict):
        name = qds_data.get("name")
        if not name:
            raise ValueError("name not specified")

        desc = qds_data.get("desc", "")
        created_at = qds_data.get("created_at", "")

        toml_doc = self.load_config()

        qds_command = tomlkit.table()
        qds_command.add("desc", desc)
        qds_command.add("created_at", created_at)

        toml_doc[name] = qds_command
        self.save_config(toml_doc)

    def update(self, name: str, new_data: dict):
        toml_doc = self.load_config()

        if name not in toml_doc:
            raise KeyError(f"No entry named '{name}' found")

        for key in ["desc", "created_at"]:
            if key in new_data:
                toml_doc[name][key] = new_data[key]

        self.save_config(toml_doc)

    def rename(self, old_name: str, new_name: str):
        if old_name == new_name:
            raise ValueError("Old name and new name are the same")

        toml_doc = self.load_config()

        toml_doc[new_name] = toml_doc[old_name]
        del toml_doc[old_name]

        self.save_config(toml_doc)

    def delete(self, name: str):
        toml_doc = self.load_config()

        if name not in toml_doc:
            raise KeyError(f"No entry named '{name}' to delete")

        del toml_doc[name]
        self.save_config(toml_doc)

    def list_all_scripts(self):
        toml_dict = self.load_config().value

        return [*toml_dict.keys()]

    def get_script_data(self, name: str):
        toml_dict = self.load_config().value

        return toml_dict[name]
