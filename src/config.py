# Built-in Libraries
import logging.config
import sys
from pathlib import Path

# Third Party Libraries
from ruamel.yaml import YAML

yaml = YAML(typ="safe")

# Local Libraries
# N/A

# ==============================================================================
# Determine where we are running
# ==============================================================================
if getattr(sys, "frozen", False):
	_BASEDIR = Path(sys.executable).parent
	_ASSETS_DIR = Path(sys._MEIPASS) / "assets"
else:
	_BASEDIR = Path(__file__).parent
	_ASSETS_DIR = _BASEDIR / "assets"

# ==============================================================================
# Assets
# ==============================================================================
APP_ICON = _ASSETS_DIR / "app.ico"

# ==============================================================================
# Config Files
# ==============================================================================
_CONFIGS_DIR = _BASEDIR / "configs"

ADDONS_CONFIG = _CONFIGS_DIR / "addons.yaml"
SETTINGS_CONFIG = _CONFIGS_DIR / "settings.yaml"
LOGGING_CONFIG = _CONFIGS_DIR / "logging.yaml"

# ==============================================================================
# Logs
# ==============================================================================
LOGS_DIR = _BASEDIR / "logs"


# ==============================================================================
# Helpers
# ==============================================================================
def relpath(p: Path) -> Path:
	return p.relative_to(_BASEDIR)


# ==============================================================================
# Configure (and fix) Logging
# ==============================================================================
def initialize():
	if hasattr(initialize, "ran"):
		logging.warning("Unnecessary extra call to config.initialize")
		return

	from parsers.logging import load

	logging.config.dictConfig(load())

	initialize.ran = True
