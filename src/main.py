# Python 3.13
# ==============================================================================
# Built-in Libraries
import logging

# a rough spitball of what I'm thinking about and what I'll need...
# GOAL:
# 	create a simple UI to install and uninstall gw2 addons from various sources
#	configurations of this app should be handled via YAML when possible
#	allow users to select which addons they want to install/uninstall

# create a config module
#	all configurations will come from YAML
#		separate parser logic to keep things clean
# 	configs...
#		- logging*: how I want logs to look
#		- assets*: probably just icon paths
#		- settings*: extra user settings
#		*This program will be an EXE so MEIPASS path tweaks will be needed
# separate gui controls
# separate api controls

# ==============================================================================
def main():
	pass

# ==============================================================================
if __name__ == "__main__":
	main()
