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

from parsers import addons

# a rough spitball of what I'm thinking about and what I'll need...
# GOAL:
# 	create a simple UI to install and uninstall gw2 addons from various sources
#	configurations of this app should be handled via YAML when possible
#	allow users to select which addons they want to install/uninstall

# separate gui controls

# ==============================================================================
def main():
	pass

# ==============================================================================
if __name__ == "__main__":
	main()
