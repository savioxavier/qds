from pathlib import Path

from .config import QdsConfig
from .log import QdsLogger

HOMEDIR = Path.home()

QDS_DIR = HOMEDIR / ".qds"

QDS_CONFIG_FILE = QDS_DIR / "qds.toml"

QDS_INITIAL_CONTENTS = """
from qds_run import qds


@qds(
    args=[("text", str, "Sample text to be provided")],
)
def run(text: str) -> str:
    pass

""".strip()


logger = QdsLogger()
qds_config = QdsConfig(config_path=QDS_CONFIG_FILE)
