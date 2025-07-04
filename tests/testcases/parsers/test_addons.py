# Built-in Libraries
# N/A

# Third Party Libraries
# N/A

# Local Libraries
from parsers.addons import load


# ==============================================================================
class TestAddons:
	# --------------------------------------------------------------------------
	def test_load_addons(self):
		assert load()
