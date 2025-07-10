# Built-in Libraries
import sys
from pathlib import Path

# Third Party Libraries
# N/A

# Local Libraries
# N/A

# ==============================================================================
# Determine where we are running
# ==============================================================================
if getattr(sys, "frozen", False):
	BASEDIR = Path(sys.executable).parent
	ASSETS_DIR = Path(sys._MEIPASS) / "assets"
else:
	BASEDIR = Path(__file__).parent
	ASSETS_DIR = BASEDIR / "assets"

# ==============================================================================
# Assets
# ==============================================================================
APP_ICON = ASSETS_DIR / "app.ico"

# ==============================================================================
# Config Files
# ==============================================================================
CONFIGS_DIR = BASEDIR / "configs"

ADDONS_CONFIG = CONFIGS_DIR / "addons.yaml"
SETTINGS_CONFIG = CONFIGS_DIR / "settings.yaml"
LOGGING_CONFIG = CONFIGS_DIR / "logging_config.yaml"

LOGS_DIR = BASEDIR / "logs"


# ==============================================================================
# Helpers
# ==============================================================================
def relpath(p: Path) -> Path:
	return p.relative_to(BASEDIR)
