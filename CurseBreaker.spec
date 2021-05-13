# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['CurseBreaker.py'],
             pathex=['/Users/tak/git/CRIT'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['Hooks/'],
             runtime_hooks=[],
             excludes=['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='CurseBreaker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='CurseBreaker.ico')
