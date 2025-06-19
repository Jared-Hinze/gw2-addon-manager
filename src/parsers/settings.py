# Python 3.13
# ==============================================================================
# Built-in Libraries
import logging
import json
import re
from pathlib import Path

# Third Party Libraries
# N/A

# Local Libraries
from config import SETTINGS_CONFIG, relpath
from parsers import load_yaml

# ==============================================================================
# Initializers
# ==============================================================================
logger = logging.getLogger(__name__)

# ==============================================================================
# Classes
# ==============================================================================
class Settings(dict):
	# --------------------------------------------------------------------------
	def __repr__(self):
		attrs = ", ".join(f"{k}={v!r}" for k, v in self.items())
		return f"{type(self).__name__}({attrs})"

# ==============================================================================
# Helpers
# ==============================================================================
def fqn(key):
	return f"[{SETTINGS_CONFIG}@{key}]"

# ------------------------------------------------------------------------------
def ensure_key(settings, key):
	if key not in settings:
		logger.critical("Missing Key.")
		logger.critical(f"See: {fqn(key)}")
		return False
	return True

# ------------------------------------------------------------------------------
def ensure_path(settings, key):
	if not ensure_key(settings, key):
		return

	value = settings[key]
	try:
		value = settings[key] = Path(str(value))
	except Exception:
		logger.error(f'Failed to convert "{value}" to Path.')
		logger.error(f"See {fqn(key)}.")
		return

	if not value.exists():
		logger.error(f'Invalid Path "{value}".')
		logger.error(f"See {fqn(key)}.")

# ==============================================================================
# Loader
# ==============================================================================
def load():
	if not SETTINGS_CONFIG.exists():
		logger.critical(f"Missing File: {relpath(SETTINGS_CONFIG)}")
		return Settings()

	settings = Settings(load_yaml(SETTINGS_CONFIG))
	ensure_path(settings, "install_path")

	return settings
