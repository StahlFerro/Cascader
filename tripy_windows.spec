# -*- mode: python ; coding: utf-8 -*-


import PyInstaller.config
PyInstaller.config.CONF['distpath'] = "./engine/"
block_cipher = None


added_files = [
    ('bin/gifsicle-1.92-win64/gifsicle.exe', 'bin/gifsicle-1.92-win64/'),
    ('bin/ImageMagick-7.0.8-61-win/convert.exe', 'bin/ImageMagick-7.0.8-61-win/'),
    ('cache/.include', 'cache/'),
    ('temp/.include', 'temp/'),
    ('config/config.json', 'config/')
]
a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='windows')
