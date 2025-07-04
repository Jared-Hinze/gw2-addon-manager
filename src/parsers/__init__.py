# Built-in Libraries
import logging
from typing import TYPE_CHECKING

# Third Party Libraries
# N/A

# Local Libraries
from config import relpath, yaml

# Type Checking
if TYPE_CHECKING:
	from pathlib import Path

# ==============================================================================
# Initializers
# ==============================================================================
logger = logging.getLogger(__name__)


# ==============================================================================
# Shared Helpers
# ==============================================================================
def is_missing_file(file: "Path"):
	if not file.exists():
		logger.critical(f"Missing File: {relpath(file)}")
		return True
	return False


# ------------------------------------------------------------------------------
def load_yaml(file: "Path") -> dict | None:
	data = None

	try:
		with file.open() as f:
			data = yaml.load(f)

			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(data)
	except Exception as e:
		logger.exception(e)

	return data


# ==============================================================================
# Pre-loaders
# ==============================================================================
from . import settings

Settings = settings.load()

from . import addons

addons = addons.load()
