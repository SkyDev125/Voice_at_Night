# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = [('resources/images/icon.ico', 'resources/images/'), ('venv/Lib/site-packages/whisper/assets/', 'whisper/assets/')]
datas += collect_data_files('sv_ttk')
datas += copy_metadata('openai-whisper', recursive=True)


a = Analysis(
    ['ui.pyw'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['tiktoken_ext.openai_public', 'tiktoken_ext'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    'resources/images/icon.ico',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=False,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [],
    name='MagicSpeech',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\images\\icon.ico'],
)
