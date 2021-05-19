import sys
import pkgutil
import os
from importlib import import_module

import importlib
import pkgutil
import sys

from CRIT import commands
def load_commands(character, session, console):
    for mod_name in _iter_namespace(commands):
        short_name = mod_name.split('.')[2]

        # Ensure that module isn't already loaded
        if mod_name not in sys.modules:
            # Import module
            loaded_mod = import_module(mod_name)

            # Load class from imported module
            class_name = ''.join([x.title() for x in short_name.split('_')])
            print(class_name)
            loaded_class = getattr(loaded_mod, class_name, None)
            print(loaded_class)
            if not loaded_class:
                continue

            # Create an instance of the class
            instance = loaded_class(character, session, console)
            print(instance)

def _iter_namespace(nsp):
    """
    Return an iterator of names of modules found in a specific namespace.
    The names are made absolute, with the namespace as prefix, to simplify
    import.
    """
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    prefix = nsp.__name__ + "."
    # for pkg in pkgutil.iter_modules(nsp.__path__, prefix):
    #     yield pkg[1]  # pkg is (finder, name, ispkg)
    # special handling when the package is bundled with PyInstaller
    # See https://github.com/pyinstaller/pyinstaller/issues/1905
    toc = set()  # table of content
    for importer in pkgutil.iter_importers(nsp.__name__.partition(".")[0]):
        print(importer)
        if hasattr(importer, 'toc'):
            toc |= importer.toc
    for name in toc:
        if name.startswith(prefix):
            yield name