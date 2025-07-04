# Note:
# This file will never import logging since its job is to provide the logging
# module the necessary configuration. All output will be routed to stdout.

# Built-in Libraries
# N/A

# Third Party Libraries
# N/A

# Local Libraries
from config import LOGGING_CONFIG, LOGS_DIR, yaml
from parsers import is_missing_file


# ==============================================================================
def load() -> dict:
	if is_missing_file(LOGGING_CONFIG):
		return {}

	with LOGGING_CONFIG.open() as f:
		data = yaml.load(f)

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
