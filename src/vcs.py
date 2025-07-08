# Built-in Libraries
import requests
import sys
import tomllib

# Third Party Libraries
from semver.version import Version
from win32api import GetFileVersionInfo, HIWORD, LOWORD

# Local Libraries
import api
from paths import BASEDIR


# ==============================================================================
def get_local_version():
	# Actually running the EXE
	if getattr(sys, "frozen", False):
		info = GetFileVersionInfo(sys.executable, "\\")

		ms32_version = info['FileVersionMS']  # most significant 32 bits
		ls32_version = info['FileVersionLS']  # least significant 32 bits

		return Version(
			major=HIWORD(ms32_version),
			minor=LOWORD(ms32_version),
			patch=HIWORD(ls32_version),
			prerelease=LOWORD(ls32_version),
		)

	# In Development
	with (BASEDIR.parent / "pyproject.toml").open("rb") as f:
		return Version.parse(tomllib.load(f)["project"]["version"])


# ------------------------------------------------------------------------------
def get_remote_version():
	response = requests.get(api.app_tags_url())
	tags = (Version.parse(tag["name"].lstrip('v')) for tag in response.json())
	return next(iter(sorted(tags, reverse=True)))


# ------------------------------------------------------------------------------
def has_update():
	return get_remote_version() > get_local_version()
