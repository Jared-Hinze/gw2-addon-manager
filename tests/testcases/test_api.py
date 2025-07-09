# Built-in Libraries
import logging
import requests
from zipfile import ZipFile

# Third Party Libraries
from hypothesis import given, strategies as st
from pytest import fixture, raises

# Local Libraries
import api
from api import ApiException, AssetType
from helpers import has_message


# ==============================================================================
# Fixtures
# ==============================================================================
@fixture(scope="function")
def test_url():
	return "http://test1.com"


# ------------------------------------------------------------------------------
@fixture(scope="function")
def redirect_url():
	return "http://test2.com"


# ------------------------------------------------------------------------------
@fixture(scope="function")
def fake_dll():
	return "foo.dll"


# ------------------------------------------------------------------------------
@fixture(scope="function")
def svc_direct(tmp_path, test_url, fake_dll):
	return api.DirectRequest(test_url, fake_dll, tmp_path / fake_dll)


# ------------------------------------------------------------------------------
@fixture(scope="function")
def svc_git(tmp_path, test_url, fake_dll):
	return api.GitRequest(test_url, fake_dll, tmp_path / fake_dll)


# ==============================================================================
# Tests
# ==============================================================================
def test_direct_request_get_asset_dll(requests_mock, svc_direct):
	"""Ensure we get a Response and AssetType.DLL"""
	requests_mock.get(svc_direct.url)

	resp, asset_type = svc_direct.get_asset()
	assert resp
	assert asset_type == AssetType.DLL


# ------------------------------------------------------------------------------
def test_direct_request_download_dll(requests_mock, svc_direct):
	"""Ensure the DLL is written to dst"""
	content = b"foo"

	requests_mock.get(svc_direct.url, content=content)

	svc_direct.download()
	assert svc_direct.dst.exists()
	assert svc_direct.dst.read_bytes() == content


# ------------------------------------------------------------------------------
def test_git_request_check_invalid_status_code(requests_mock, capsys, svc_git):
	"""Ensure we raise when response.status_code is 500"""
	requests_mock.get(svc_git.url, status_code=500)

	with raises(AssertionError):
		assert svc_git.check(requests.get(svc_git.url))
		assert has_message(capsys, "Error: status_code")


# ------------------------------------------------------------------------------
def test_git_request_check_no_assets(requests_mock, capsys, svc_git):
	"""Ensure we raise when the response does not contain the "assets" key"""
	requests_mock.get(svc_git.url, status_code=200, json={})

	with raises(AssertionError):
		assert svc_git.check(requests.get(svc_git.url))
		assert has_message(capsys, 'Error: Missing key')


# ------------------------------------------------------------------------------
def test_git_request_check_invalid(requests_mock, svc_git):
	"""Ensure we raise when we don't get a JSON object back"""
	requests_mock.get(svc_git.url, status_code=200)

	with raises(requests.exceptions.JSONDecodeError):
		assert svc_git.check(requests.get(svc_git.url))


# ------------------------------------------------------------------------------
def test_git_request_check_valid(requests_mock, svc_git):
	"""Ensure we return a JSON object when response.status_code is 200"""
	requests_mock.get(svc_git.url, status_code=200, json={"assets": []})

	assert svc_git.check(requests.get(svc_git.url))


# ------------------------------------------------------------------------------
def test_git_request_call_api_failed(requests_mock, caplog, svc_git):
	"""Ensure we see the message "Max retries exceeded" on failure"""
	requests_mock.get(svc_git.url, status_code=500)

	with raises(ApiException, match="Max retries exceeded"):
		svc_git.debug = True
		svc_git.call_api(retries=2)
		assert has_message(caplog, "Error: status_code")


# ------------------------------------------------------------------------------
def test_git_request_call_api_success(requests_mock, svc_git):
	"""Ensure we return a dictionary on success"""
	requests_mock.get(svc_git.url, status_code=200, json={"assets": []})

	svc_git.call_api(retries=2)


# ------------------------------------------------------------------------------
def test_git_request_get_asset_not_found(requests_mock, svc_git):
	"""Raise message "Could not determine..." for indeterminable asset"""
	requests_mock.get(
		svc_git.url,
		status_code=200,
		json={"assets": [{"name": "bar.dll"}]},
	)

	with raises(ApiException, match="Could not determine Git API asset"):
		svc_git.get_asset()


# ------------------------------------------------------------------------------
def test_git_request_no_asset(requests_mock, svc_git):
	"""A failed call will raise an ApiException"""
	requests_mock.get(svc_git.url, status_code=200, json={"assets": []})

	with raises(ApiException, match="Could not determine Git API asset"):
		svc_git.get_asset()


# ------------------------------------------------------------------------------
def test_git_request_get_asset_dll(requests_mock, caplog, svc_git, redirect_url):
	"""A successful call will return a Response and AssetType.DLL"""
	caplog.set_level(logging.DEBUG)

	# First call to git API will result in a redirect URL key
	requests_mock.get(
		svc_git.url,
		status_code=200,
		json={
			"assets": [
				{
					"name": svc_git.dll,
					"browser_download_url": redirect_url,
				},
			],
		},
	)
	# Actual call happens here
	requests_mock.get(redirect_url, status_code=200)

	svc_git.debug = True
	response, asset_type = svc_git.get_asset()
	assert response
	assert asset_type == AssetType.DLL
	assert has_message(caplog, "redirected to")


# ------------------------------------------------------------------------------
def test_git_request_get_asset_zip(requests_mock, caplog, svc_git, redirect_url):
	"""A successful call will return a Response and AssetType.ZIP"""
	caplog.set_level(logging.DEBUG)

	# First call to git API will result in a redirect URL key
	requests_mock.get(
		svc_git.url,
		status_code=200,
		json={
			"assets": [
				{
					"name": "foo-windows-gnu.zip",
					"browser_download_url": redirect_url,
				},
			],
		},
	)
	# Actual call happens here
	requests_mock.get(redirect_url, status_code=200)

	svc_git.debug = True
	response, asset_type = svc_git.get_asset()
	assert response
	assert asset_type == AssetType.ZIP
	assert has_message(caplog, "redirected to")


# ------------------------------------------------------------------------------
def test_git_request_download_bad_status_code(requests_mock, svc_git, redirect_url):
	"""A non-200 status code should raise an Exception"""
	last_status_code = 500

	# First call to git API will result in a redirect URL key
	requests_mock.get(
		svc_git.url,
		status_code=200,
		json={
			"assets": [
				{
					"name": svc_git.dll,
					"browser_download_url": redirect_url,
				},
			],
		},
	)
	# Actual call happens here
	requests_mock.get(redirect_url, status_code=last_status_code)

	with raises(Exception, match=f"{svc_git.dll} got response {last_status_code}"):
		svc_git.download()


# ------------------------------------------------------------------------------
def test_git_request_download_dll(requests_mock, svc_git, redirect_url):
	"""A successful download will write the DLL"""
	final_content = b"foo"

	# First call to git API will result in a redirect URL key
	requests_mock.get(
		svc_git.url,
		status_code=200,
		json={
			"assets": [
				{
					"name": svc_git.dll,
					"browser_download_url": redirect_url,
				},
			],
		},
	)
	# Actual call happens here
	requests_mock.get(redirect_url, status_code=200, content=final_content)

	svc_git.download()
	assert svc_git.dst.exists()
	assert svc_git.dst.read_bytes() == final_content


# ------------------------------------------------------------------------------
def test_git_request_download_zip(requests_mock, svc_git, redirect_url):
	"""A successful download will write the Zip File"""
	zipf = svc_git.dst.parent / "foo.zip"
	dll, content = svc_git.dll, b"biz"
	with ZipFile(zipf, 'w') as zf:
		zf.writestr(dll, content)

	# First call to git API will result in a redirect URL key
	requests_mock.get(
		svc_git.url,
		status_code=200,
		json={
			"assets": [
				{
					"name": "foo-windows-gnu.zip",
					"browser_download_url": redirect_url,
				},
			],
		},
	)
	# Actual call happens here
	requests_mock.get(redirect_url, status_code=200, content=zipf.read_bytes())

	svc_git.download()
	assert svc_git.dst.exists()
	assert svc_git.dst.read_bytes() == content


# ------------------------------------------------------------------------------
@given(owner=st.text(), repo=st.text())
def test_git_latest_release_url(owner, repo):
	url = api.git_latest_release_url(owner, repo)
	assert url == f"https://api.github.com/repos/{owner}/{repo}/releases/latest"


# ------------------------------------------------------------------------------
@given(owner=st.text(), repo=st.text())
def test_git_tags_url(owner, repo):
	url = api.git_tags_url(owner, repo)
	assert url == f"https://api.github.com/repos/{owner}/{repo}/tags"


# ------------------------------------------------------------------------------
def test_app_latest_release_url():
	url = api.app_latest_release_url()
	assert url == "https://github.com/Jared-Hinze/gw2-addon-manager/releases/latest"


# ------------------------------------------------------------------------------
def test_app_tags_url():
	url = api.app_tags_url()
	assert url == "https://api.github.com/repos/Jared-Hinze/gw2-addon-manager/tags"
