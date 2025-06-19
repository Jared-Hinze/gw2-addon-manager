# Python 3.13
# ==============================================================================
# Built-in Libraries
import logging

# Third Party Libraries
# N/A

# Local Libraries
from config import yaml

# ==============================================================================
# Initializers
# ==============================================================================
logger = logging.getLogger(__name__)

# ==============================================================================
# Shared Helpers
# ==============================================================================
def load_yaml(file) -> dict | None:
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
