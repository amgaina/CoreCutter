# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('pages', 'pages'), ('mse_logo.png', '.'), ('app.py', '.')]
binaries = []
hiddenimports = ['streamlit', 'streamlit.runtime', 'streamlit.web', 'streamlit.web.cli', 'streamlit.runtime.scriptrunner', 'streamlit.runtime.scriptrunner.script_runner', 'PIL', 'PIL._imagingtk', 'PIL._tkinter_finder', 'ortools', 'ortools.linear_solver', 'ortools.linear_solver.pywraplp']
datas += copy_metadata('streamlit')
datas += copy_metadata('altair')
datas += copy_metadata('pillow')
datas += copy_metadata('ortools')
datas += copy_metadata('protobuf')
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CoreCut',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['mse_logo.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CoreCut',
)
app = BUNDLE(
    coll,
    name='CoreCut.app',
    icon='mse_logo.png',
    bundle_identifier=None,
)
