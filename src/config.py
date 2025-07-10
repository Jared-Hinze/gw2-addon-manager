# Built-in Libraries
import logging.config

# Third Party Libraries
# N/A

# Local Libraries
from parsers import addons, logging_config, settings

# ==============================================================================
if not logging._handlers:
	logging.config.dictConfig(logging_config.load())

# Cached
Settings = settings.load()
addons = addons.load(Settings)
