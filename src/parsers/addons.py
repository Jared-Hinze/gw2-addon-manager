# This file is to parse addons.yaml and automatically make the result a class
# object by leveraging @yaml.register_class and the yaml_tag class attribute.
#
# Note:
# I chose to do it this way primarily just because I wanted to play around with
# this feature of Python YAML parsing - not because it was needed.

# Built-in Libraries
import logging

# Third Party Libraries
# N/A

# Local Libraries
import api
from parsers import load_yaml, yaml
from paths import ADDONS_CONFIG

# ==============================================================================
# Initializers
# ==============================================================================
logger = logging.getLogger(__name__)


# ==============================================================================
# Classes
# ==============================================================================
class CoreAddon:
	# --------------------------------------------------------------------------
	@classmethod
	def from_yaml(cls, loader, node):
		return cls(**loader.construct_mapping(node, deep=True))


# ==============================================================================
class Addon(CoreAddon):
	Settings = None

	# --------------------------------------------------------------------------
	def __init__(self, url, dll, dst=''):
		self.url = url
		self.dll = dll
		self.dst = self.Settings.install_path / dst / dll
		self.removed = False

	# --------------------------------------------------------------------------
	def __repr__(self):
		attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
		return f"{type(self).__name__}({attrs})"

	# --------------------------------------------------------------------------
	@property
	def installed(self):
		return self.dst.exists()

	# --------------------------------------------------------------------------
	def install(self):
		if self.yaml_tag == "!RawAddon":
			svc = api.DirectRequest(self.url, self.dll, self.dst)
		else:
			svc = api.GitRequest(self.url, self.dll, self.dst)
		svc.download()
		self.removed = False

	# --------------------------------------------------------------------------
	def uninstall(self):
		if self.installed:
			self.dst.unlink()
			self.removed = True


# ==============================================================================
@yaml.register_class
class RawAddon(Addon):
	yaml_tag = "!RawAddon"


# ==============================================================================
@yaml.register_class
class GitAddon(Addon):
	yaml_tag = "!GitAddon"

	# --------------------------------------------------------------------------
	def __init__(self, dll, owner, repo, dst=''):
		super().__init__(api.git_latest_release_url(owner, repo), dll, dst)


# ==============================================================================
def load(Settings) -> list[Addon]:
	if getattr(load, "cache", None):
		return load.cache

	addons = []

	if not ADDONS_CONFIG.exists():
		return addons

	if not Settings:
		return addons

	install_path = Settings.install_path
	if not (install_path and install_path.exists()):
		return addons

	try:
		Addon.Settings = Settings
		addons = load_yaml(ADDONS_CONFIG)
	except Exception:
		return addons

	load.cache = sorted(addons, key=lambda addon: (addon.dst.parent, addon.dll))

	return load.cache
