# Built-in Libraries
from pathlib import Path

# Third Party Libraries
from pytest import fixture

# Local Libraries
from parsers import settings, addons


# ==============================================================================
# Fixtures
# ==============================================================================
@fixture(scope="module")
def Addon():
	addons.Addon.Settings = settings.load()

	# --------------------------------------------------------------------------
	def factory(*args, **kwargs):
		return addons.Addon(*args, **kwargs)

	return factory


# ==============================================================================
# Tests
# ==============================================================================
def test_load_missing_config(mocker):
	"""If ADDONS_CONFIG is missing expect an empty list"""
	mocker.patch("parsers.addons.ADDONS_CONFIG", Path("<foo>"))

	assert addons.load(None) == []


# ------------------------------------------------------------------------------
def test_load_no_settings():
	"""If no settings are given expect an empty list"""
	assert addons.load(None) == []


# ------------------------------------------------------------------------------
def test_load_no_install_path():
	"""If no install_path in Settings then expect an empty list"""
	assert addons.load(settings.Settings()) == []


# ------------------------------------------------------------------------------
def test_load_bad_install_path():
	"""If a bad install_path is given in Settings then expect an empty list"""
	assert addons.load(settings.Settings({"install_path": Path("<foo>")})) == []


# ------------------------------------------------------------------------------
def test_load_bad_config(mocker, tmp_path):
	"""If a bad config is loaded expect an empty list"""
	tmp_file = tmp_path / "foo.yaml"
	with tmp_file.open('w') as f:
		f.write("]:[")  # bad YAML

	mocker.patch("parsers.addons.ADDONS_CONFIG", tmp_file)

	assert addons.load(settings.Settings({"install_path": tmp_file})) == []


# ------------------------------------------------------------------------------
def test_load_good_config():
	"""If a good config is loaded expect a proper data structure"""
	assert addons.load(settings.load()) is not None


# ------------------------------------------------------------------------------
def test_addon_not_installed(Addon):
	"""If Addon.dst does not exist expect False"""
	addon = Addon(None, "foo.dll")
	assert addon.installed is False


# ------------------------------------------------------------------------------
def test_addon_installed(tmp_path, Addon):
	"""If Addon.dst does exist expect True"""
	dll = tmp_path / "foo.dll"
	dll.touch()

	addon = Addon(None, dll)

	assert addon.installed is True


# ------------------------------------------------------------------------------
def test_addon_uninstall(tmp_path, Addon):
	"""If Addon.dst is installed remove it"""
	dll = tmp_path / "foo.dll"
	dll.touch()

	addon = Addon(None, dll)
	addon.uninstall()

	assert addon.installed is False
	assert addon.removed is True
