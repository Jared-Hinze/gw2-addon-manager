# Built-in Libraries
import logging
import tomllib
from unittest import mock

# Third Party Libraries
from hypothesis import given, strategies as st
from semver.version import Version

# Local Libraries
import api
import vcs
from helpers import has_message
from paths import BASEDIR

# ==============================================================================
# Strategies
# ==============================================================================
st_semver_ints = st.integers(min_value=0, max_value=2**15 - 1)  # signed int


# ==============================================================================
# Tests
# ==============================================================================
def test_get_local_version_dev():
	"""Ensure the pyproject.toml project version follows semver standards"""
	with (BASEDIR.parent / "pyproject.toml").open("rb") as f:
		version = Version.parse(tomllib.load(f)["project"]["version"])

	assert vcs.get_local_version() == version


# ------------------------------------------------------------------------------
@given(
	major=st_semver_ints,
	minor=st_semver_ints,
	patch=st_semver_ints,
)
def test_get_local_version_exe(major, minor, patch):
	"""Ensure sys.executable parses to a proper Version"""
	with mock.patch.object(vcs.sys, "frozen", create=True, new=True):
		assert hasattr(vcs.sys, "frozen")

		version_info = {
			#      win32api: HIWORD(65538): 1 | LOWORD(65538): 2
			#              : ----------------- -----------------  ↖
			# 32 bit string: 00000000 00000001 00000000 00000010 = 65538
			"FileVersionMS": (major << 16) + minor,
			"FileVersionLS": (patch << 16),
		}
		with mock.patch("vcs.GetFileVersionInfo", return_value=version_info):
			version = vcs.get_local_version()
			assert isinstance(version, Version)
			assert version == Version(major, minor, patch)


# ------------------------------------------------------------------------------
def test_get_remote_version(requests_mock):
	"""Ensure we get the latest remote version"""
	requests_mock.get(
		api.app_tags_url(),
		json=[
			{"name": "v1.1.0"},
			{"name": "v1.3.1"},
			{"name": "v1.0.0"},
		],
	)

	assert vcs.get_remote_version() == Version(1, 3, 1)


# ------------------------------------------------------------------------------
def test_has_update_newer(requests_mock, mocker):
	"""Return True when get_remote_version > get_local_version"""
	requests_mock.get(api.app_tags_url(), json=[{"name": "v1.0.0"}])
	mocker.patch("vcs.get_local_version", return_value=Version(0))

	assert vcs.has_update() is True


# ------------------------------------------------------------------------------
def test_has_update_older(requests_mock, mocker):
	"""Return False when get_remote_version > get_local_version"""
	requests_mock.get(api.app_tags_url(), json=[{"name": "v1.0.0"}])
	mocker.patch("vcs.get_local_version", return_value=Version(2))

	assert vcs.has_update() is False


# ------------------------------------------------------------------------------
def test_has_update_same(requests_mock, mocker):
	"""Return False when get_remote_version == get_local_version"""
	requests_mock.get(api.app_tags_url(), json=[{"name": "v1.0.0"}])
	mocker.patch("vcs.get_local_version", return_value=Version(1))

	assert vcs.has_update() is False


# ------------------------------------------------------------------------------
def test_has_update_logging(requests_mock, mocker, caplog):
	"""Making sure this message gets logged in case I need to troubleshoot"""
	requests_mock.get(api.app_tags_url(), json=[{"name": "v1.0.0"}])
	mocker.patch("vcs.get_local_version", return_value=Version(1))
	caplog.set_level(logging.DEBUG)

	vcs.has_update()
	assert has_message(caplog, "Version Checking")
