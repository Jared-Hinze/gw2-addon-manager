# Built-in Libraries
import re
from pathlib import Path

# Third Party Libraries
from pytest import fixture
from hypothesis import given, strategies as st

# Local Libraries
import parsers.settings as settings
from config import SETTINGS_CONFIG
from helpers import has_message


# ==============================================================================
# Fixtures
# ==============================================================================
@fixture(scope="module")
def Settings():
	def factory(*args, **kwargs):
		return settings.Settings(*args, **kwargs)

	return factory


# ==============================================================================
# Strategy Helpers
# ==============================================================================
def bool_strats(strat):
	return (strat.map(str.lower), strat.map(str.upper), strat.map(str.title))


# ==============================================================================
# Strategies
# ==============================================================================
# YAML Boolean Value Matching
true_rgx = re.compile(r"yes|true|on|[ty]")
false_rgx = re.compile(r"no|false|off|[fn]")

st_trues = st.from_regex(true_rgx, fullmatch=True)
st_falses = st.from_regex(false_rgx, fullmatch=True)
st_yaml_booleans = st.one_of(*bool_strats(st_trues), *bool_strats(st_falses))


# ==============================================================================
# Tests
# ==============================================================================
def test_settings_class_no_values_truthiness(Settings):
	"""Empty Settings should be False"""
	assert bool(Settings()) is False


# ------------------------------------------------------------------------------
def test_settings_class_with_values_truthiness(Settings):
	"""Settings with values should be True"""
	assert bool(Settings({"key": 1})) is True


# ------------------------------------------------------------------------------
def test_load_missing_config(mocker, caplog, Settings):
	"""Expect Settings() if SETTINGS_CONFIG does not exist"""
	mocker.patch("config.SETTINGS_CONFIG", SETTINGS_CONFIG.with_name("foo"))
	assert settings.load() == Settings()
	assert has_message(caplog, "Missing File")


# ------------------------------------------------------------------------------
def test_load_existing_config():
	"""If SETTINGS_CONFIG exists we should get a filled Settings object"""
	assert settings.load()


# ------------------------------------------------------------------------------
@given(key=st.text())
def test_fqn(key):
	"""Ensure fqn provides logs full path information to key"""
	assert settings.fqn(key) == f"[{SETTINGS_CONFIG}@{key}]"


# ------------------------------------------------------------------------------
def test_ensure_key_missing(caplog, Settings):
	"""If a key is missing return False and log it"""
	assert settings.ensure_key(Settings(), "<foo>") is False
	assert has_message(caplog, "Missing Key")


# ------------------------------------------------------------------------------
def test_ensure_key_present(Settings):
	"""If a key exists return True"""
	key = "<foo>"
	assert settings.ensure_key(Settings({key: "bar"}), key) is True


# ------------------------------------------------------------------------------
def test_ensure_bool_missing_key(caplog, Settings):
	"""Bail if a key doesn't exist. Should leave config untouched"""
	config = Settings()
	settings.ensure_bool(config, "<foo>")
	assert config == Settings()
	assert has_message(caplog, "Missing Key")


# ------------------------------------------------------------------------------
def test_ensure_bool_invalid_key_value(caplog, Settings):
	"""Set key to None if it is not a YAML boolean and log it"""
	key = "<foo>"
	config = Settings({key: "<bar>"})
	settings.ensure_bool(config, key)
	assert config[key] is None
	assert has_message(caplog, "Invalid Value")


# ------------------------------------------------------------------------------
@given(value=st_yaml_booleans)
def test_ensure_bool_valid_key_value(Settings, value):
	"""Ensure valid YAML boolean string is converted to a proper bool object"""
	key = "<foo>"
	config = Settings({key: value})
	settings.ensure_bool(config, key)
	assert isinstance(config[key], bool)


# ------------------------------------------------------------------------------
def test_ensure_path_missing_key(caplog, Settings):
	"""Bail if a key doesn't exist. Should leave config untouched"""
	config = Settings()
	settings.ensure_path(config, "<foo>")
	assert config == Settings()
	assert has_message(caplog, "Missing Key")


# ------------------------------------------------------------------------------
def test_ensure_path_fail_conversion(caplog, tmp_path, Settings):
	"""Set key to None if it is not a Pathlike object and log it"""
	key = "<foo>"
	config = Settings({key: 1.2})
	settings.ensure_path(config, key)
	assert config[key] is None
	assert has_message(caplog, "Failed to convert")


# ------------------------------------------------------------------------------
def test_ensure_path_when_does_not_exist(caplog, Settings):
	"""Set key to None if the path does not exist and log it"""
	key = "<foo>"
	config = Settings({key: str(Path("<bar>"))})
	settings.ensure_path(config, key)
	assert config[key] is None
	assert has_message(caplog, "Path does not exist")


# ------------------------------------------------------------------------------
def test_ensure_path_valid_key_value(tmp_path, Settings):
	"""Ensure valid Pathlike string is converted to a proper Path object"""
	key = "<foo>"
	config = Settings({key: str(tmp_path)})
	settings.ensure_path(config, key)
	assert isinstance(config[key], Path)
