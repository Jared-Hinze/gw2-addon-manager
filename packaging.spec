# -*- mode: python ; coding: utf-8 -*-
# Python 3.13
# ==============================================================================
# Built-in Libraries
import shutil
from pathlib import Path

# Third Party Libraries
# N/A

# Local Libraries
# N/A

# ==============================================================================
# Globals
# ==============================================================================
ROOT = Path(SPECPATH)
APP_NAME = ROOT.stem

# ==============================================================================
# Spec
# ==============================================================================
a = Analysis(
    ["src/main.py"],
    pathex=[],
    binaries=[],
    datas=[("src/assets", "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

e = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["src/assets/app.ico"],
)

# ==============================================================================
# Custom carry over of configuration files
# ==============================================================================
print("Running Custom Build Extension")
distdir = ROOT / "dist"

shutil.copytree(ROOT / "src/configs", distdir / "configs", dirs_exist_ok=True)

log = distdir / "logs/report.log"
log.parent.mkdir(exist_ok=True)
log.touch()
