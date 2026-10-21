# PyInstaller build recipe - turns the game into one MarasSiege.exe
# Build with: python -m PyInstaller mara_siege.spec --distpath dist --workpath build_tmp
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],  # No data files - all graphics and sounds are generated in code
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'email', 'html', 'http', 'xml', 'numpy'],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MarasSiege',
    debug=False,
    strip=False,
    upx=True,
    console=False,  # No terminal window behind the game
    icon=None,
)
