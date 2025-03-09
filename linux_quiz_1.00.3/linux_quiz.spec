# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['linux.py'],
    pathex=[],
    binaries=[],
    datas=[('assets\\icon\\linux afbeelding 2.png', 'assets/icon'), ('assets\\linux_questions', 'assets/linux_questions'), ('assets\\linuxbook\\*.pdf', 'assets/linuxbook'), ('assets\\linux_questions_images', 'assets/linux_questions_images')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='linux_quiz',
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
    icon=['assets\\icon\\linux_icon2.ico'],
)
