from PyInstaller.utils.hooks import collect_submodules, copy_metadata
hiddenimports = collect_submodules('CRIT.commands')
datas = copy_metadata('CRIT')