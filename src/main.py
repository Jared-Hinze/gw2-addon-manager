# Python 3.13
# ==============================================================================
# Built-in Libraries
import logging

# Third Party Libraries
# N/A

# Need to initialize logging and path constants before importing local libraries
# so dependencies that use logging can be configured by this call
import config
config.initialize()

# Local Libraries
import gui
from parsers import addons

# ==============================================================================
def main():
	logging.info("Creating GUI")

	gui.create_ui(addons)
	gui.show()

	logging.info("Closing GUI")
	logging.info('-' * 100)

# ==============================================================================
if __name__ == "__main__":
	main()
