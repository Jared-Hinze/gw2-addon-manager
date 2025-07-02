# Built-in Libraries
import logging
from abc import ABC, abstractmethod
from enum import IntEnum, auto
from io import BytesIO
from zipfile import ZipFile

# Third Party Libraries
import requests

# Local Libraries
# N/A

# ==============================================================================
# Initializers
# ==============================================================================
logger = logging.getLogger(__name__)


# ==============================================================================
class ApiException(Exception):
	pass


# ==============================================================================
class AssetType(IntEnum):
	DLL = auto()
	ZIP = auto()


# ==============================================================================
class ApiRequest(ABC):
	# --------------------------------------------------------------------------
	def __init__(self, url, dll, dst):
		self.debug = logger.isEnabledFor(logging.DEBUG)
		self.url = url
		self.dll = dll
		self.dst = dst

	# --------------------------------------------------------------------------
	@abstractmethod
	def get_asset(self) -> tuple[requests.Response, AssetType | None]:
		raise NotImplementedError

	# --------------------------------------------------------------------------
	def _get_asset(self) -> tuple[requests.Response, AssetType | None]:
		if self.debug:
			logger.debug(f"{self.dll} is contacting {self.url}")
		return self.get_asset()

	# --------------------------------------------------------------------------
	def download(self):
		response, asset_type = self._get_asset()
		if response.status_code != 200:
			raise Exception(f"{self.dll} got response {response.status_code} from {response.url}")

		if asset_type == AssetType.DLL:
			with self.dst.open("wb") as f:
				f.write(response.content)
		elif asset_type == AssetType.ZIP:
			zf = ZipFile(BytesIO(response.content))
			zf.extract(self.dll, self.dst.parent)


# ==============================================================================
class DirectRequest(ApiRequest):
	# --------------------------------------------------------------------------
	def get_asset(self) -> tuple[requests.Response, AssetType]:
		return requests.get(self.url), AssetType.DLL


# ==============================================================================
class GitRequest(ApiRequest):
	# --------------------------------------------------------------------------
	def get_asset(self) -> tuple[requests.Response, AssetType | None]:
		data = self.call_api(retries=10)

		asset = asset_type = None
		for asset in data["assets"]:
			name = asset["name"]
			if name == self.dll:
				asset_type = AssetType.DLL
			elif name.endswith("windows-gnu.zip"):
				asset_type = AssetType.ZIP
			if asset_type:
				break
		else:
			asset = None

		if not asset:
			raise ApiException("Could not determine Git API asset.")

		latest_url = asset["browser_download_url"]

		if self.debug:
			logger.debug(f"{self.dll} redirected to {latest_url}")

		return requests.get(latest_url), asset_type

	# --------------------------------------------------------------------------
	def call_api(self, *, retries) -> dict:
		for _ in range(max(1, retries)):
			try:
				return self.check(requests.get(self.url))
			except Exception as e:
				if self.debug:
					logger.error(e)
				continue

		raise ApiException("Max retries exceeded")

	# --------------------------------------------------------------------------
	def check(self, response) -> dict:
		assert response.status_code == 200
		data = response.json()
		assert "assets" in data
		return data
