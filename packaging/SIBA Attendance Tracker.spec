# PyInstaller build definition for the single-file desktop application.

from PyInstaller.utils.hooks import collect_submodules


hiddenimports = collect_submodules("webview.platforms")

a = Analysis(
    ["../src/siba_attendance_tracker/desktop.py"],
    pathex=["../src"],
    binaries=[],
    datas=[
        (
            "../src/siba_attendance_tracker/templates",
            "siba_attendance_tracker/templates",
        ),
        (
            "../src/siba_attendance_tracker/static",
            "siba_attendance_tracker/static",
        ),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SIBA Attendance Tracker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
