# Built-in Libraries
import json
from pathlib import Path

# Third Party Libraries
from pytest import fixture

# Local Libraries
from helpers import has_message
from parsers import logging_config


# ==============================================================================
# Fixtures
# ==============================================================================
@fixture(scope="function")
def tmp_yaml(tmp_path):
	def factory(filename):
		tmp_file = tmp_path / "foo.yaml"
		with tmp_file.open('w') as f:
			model = {"handlers": {"file": {"filename": filename}}}
			f.write(json.dumps(model).replace('"', ''))
		return tmp_file

	return factory


# ==============================================================================
# Tests
# ==============================================================================
def test_load_missing_config(mocker):
	"""Expect {} if LOGGING_CONFIG does not exist"""
	mocker.patch("parsers.logging_config.LOGGING_CONFIG", Path("<foo>"))

	assert logging_config.load() == {}


# ------------------------------------------------------------------------------
def test_load_bad_handler(mocker, capsys, tmp_yaml):
	"""Expect {} if LOGGING_CONFIG is malformed"""
	tmp_file = tmp_yaml(1)
	mocker.patch("parsers.logging_config.LOGGING_CONFIG", tmp_file)

	assert logging_config.load() == {}
	assert has_message(capsys, "Failed to reconfigure")


# ------------------------------------------------------------------------------
def test_load_existing_config(mocker, tmp_yaml):
	"""If LOGGING_CONFIG exists we should get a filled dict object"""
	tmp_file = tmp_yaml("foo.log")
	mocker.patch("parsers.logging_config.LOGGING_CONFIG", tmp_file)
	mocker.patch("parsers.logging_config.LOGS_DIR", tmp_file.parent)

	config = logging_config.load()
	file_handler = config["handlers"]["file"]["filename"]
	assert file_handler.exists()
	assert file_handler.relative_to(tmp_file.parent)
