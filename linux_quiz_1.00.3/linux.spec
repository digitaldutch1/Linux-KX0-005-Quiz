# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\denni\\Desktop\\linux\\linux_quiz_1.00.2\\linux.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\denni\\Desktop\\linux\\linux_quiz_1.00.2\\assets\\linux_questions', 'assets\\linux_questions'), ('C:\\Users\\denni\\Desktop\\linux\\linux_quiz_1.00.2\\assets\\linuxbook\\linuxbook.pdf', 'assets\\linuxbook')],
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
    name='linux',
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
    icon=['C:\\Users\\denni\\Desktop\\linux\\linux_quiz_1.00.2\\assets\\icon\\linux_icon2.ico'],
)