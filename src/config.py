# Python 3.13
# ==============================================================================
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
# Configure (and fix) Logging
# ==============================================================================
def initialize():
	if hasattr(initialize, "ran"):
		logging.warning("Unnecessary extra call to config.initialize")
		return

	# --------------------------------------------------------------------------
	def _fix_paths(data):
		if not data:
			return {}

		handlers = data.get("handlers") or {}
		for handler, config in handlers.items():
			try:
				if "filename" in config:
					target = LOGS_DIR / config["filename"]
					target.parent.mkdir(parents=True, exist_ok=True)
					target.touch(exist_ok=True)
					config["filename"] = target
			except Exception as e:
				# Not logged
				print(f"Failed to reconfigure {handler} with {config=}")
				print(e)

		return data

	# --------------------------------------------------------------------------
	with LOGGING_CONFIG.open() as f:
		logging.config.dictConfig(_fix_paths(yaml.load(f)))

	initialize.ran = True
