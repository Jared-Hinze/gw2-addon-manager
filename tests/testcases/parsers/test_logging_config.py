# Built-in Libraries
from pathlib import Path

# Third Party Libraries
from pytest import fixture
from hypothesis import given, strategies as st

# Local Libraries
import config
import parsers.logging_config as logging_config
from helpers import has_message


# ==============================================================================
# Tests
# ==============================================================================
def test_load_missing_config(mocker, caplog):
	"""Expect {} if LOGGING_CONFIG does not exist"""
	mocker.patch("parsers.logging_config.is_missing_file", return_value=True)
	assert logging_config.load() == {}
	# assert has_message(caplog, "Missing File")


# ------------------------------------------------------------------------------
def test_load_existing_config(mocker):
	"""If LOGGING_CONFIG exists we should get a filled dict object"""
	# mocker.patch("config.LOGGING_CONFIG", new=Path("foo"))
	# config = logging_config.load()
	# assert config
	# assert config["handlers"]
	pass
