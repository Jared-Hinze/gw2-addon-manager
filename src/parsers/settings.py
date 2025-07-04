# Built-in Libraries
import logging
import re
from pathlib import Path

# Third Party Libraries
# N/A

# Local Libraries
import config
from parsers import is_missing_file, load_yaml

# ==============================================================================
# Initializers
# ==============================================================================
logger = logging.getLogger(__name__)


# ==============================================================================
# Classes
# ==============================================================================
class Settings(dict):
	# --------------------------------------------------------------------------
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	# --------------------------------------------------------------------------
	def __repr__(self):
		attrs = ", ".join(f"{k}={v!r}" for k, v in self.items())
		return f"{type(self).__name__}({attrs})"


# ==============================================================================
# Helpers
# ==============================================================================
def fqn(key):
	return f"[{config.SETTINGS_CONFIG}@{key}]"


# ------------------------------------------------------------------------------
def ensure_key(settings, key):
	if key not in settings:
		logger.critical("Missing Key.")
		logger.critical(f"See: {fqn(key)}")
		return False
	return True


# ------------------------------------------------------------------------------
def ensure_bool(settings, key):
	if not ensure_key(settings, key):
		return

	value = str(settings[key]).lower()
	if not re.match(r"true|false|yes|no|on|off|[tfyn]", value):
		settings[key] = None
		logger.error(f"Invalid Value: {value}.")
		logger.error(f"See {fqn(key)}.")
		return

	settings[key] = value in ('t', 'y', "true", "yes", "on")


# ------------------------------------------------------------------------------
def ensure_path(settings, key):
	if not ensure_key(settings, key):
		return

	value = settings[key]
	try:
		value = Path(value)
	except Exception:
		settings[key] = None
		logger.error(f'Failed to convert "{value}" to Path.')
		logger.error(f"See {fqn(key)}.")
		return

	if not value.exists():
		settings[key] = None
		logger.error(f'Path does not exist: "{value}".')
		logger.error(f"See {fqn(key)}.")
		return

	settings[key] = value


# ==============================================================================
# Loader
# ==============================================================================
def load() -> Settings:
	if is_missing_file(config.SETTINGS_CONFIG):
		return Settings()

	settings = Settings(load_yaml(config.SETTINGS_CONFIG))
	ensure_path(settings, "install_path")
	ensure_bool(settings, "close_on_success")

	return settings
