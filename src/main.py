# Built-in Libraries
import logging

# Third Party Libraries
# N/A

# Local Libraries
import config
import gui


# ==============================================================================
def main():
	logging.info("Creating GUI")

	gui.create_ui(config.addons)
	gui.show()

	logging.info("Closing GUI")
	logging.info('-' * 100)


# ==============================================================================
if __name__ == "__main__":
	main()
