# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Inclusive Design Wizard."""

import sys
from pathlib import Path

block_cipher = None
project_dir = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('prompts', 'prompts'),
        ('core', 'core'),
        ('ui', 'ui'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.sql.default_comparator',
        'bcrypt',
        'aiohttp',
        'docx',
        'docx.shared',
        'docx.enum.text',
        'lxml',
        'lxml._elementpath',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Inclusive Design Wizard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Inclusive Design Wizard',
)

app = BUNDLE(
    coll,
    name='Inclusive Design Wizard.app',
    icon='assets/icon.icns',
    bundle_identifier='com.inclusivedesign.wizard',
    info_plist={
        'CFBundleName': 'Inclusive Design Wizard',
        'CFBundleDisplayName': 'Inclusive Design Wizard',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.15',
        'CFBundleIconFile': 'icon',
    },
)
