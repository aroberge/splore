''' A custom Importer making use of the import hook capability

https://www.python.org/dev/peps/pep-0302/

When a module is imported, it simply adds a line to its source code 
prior to execution.

This code was adapted from
http://stackoverflow.com/questions/43571737/how-to-implement-an-import-hook-that-can-modify-the-source-code-on-the-fly-using/43573798#43573798
which is a question I asked.
'''
import sys
import os.path

from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_file_location

class MyMetaFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if path is None or path == "":
            path = [os.getcwd()] # top level import -- 
        if "." in fullname:
            *parents, name = fullname.split(".")
        else:
            name = fullname
        for entry in path:
            if os.path.isdir(os.path.join(entry, name)):
                # this module has child modules
                filename = os.path.join(entry, name, "__init__.py")
                submodule_locations = [os.path.join(entry, name)]
            else:
                filename = os.path.join(entry, name + ".py")
                submodule_locations = None
            if not os.path.exists(filename):
                continue

            return spec_from_file_location(fullname, filename, loader=MyLoader(filename),
                submodule_search_locations=submodule_locations)
        return None # we don't know how to import this

class MyLoader(Loader):
    def __init__(self, filename):
        self.filename = filename

    def create_module(self, spec):
        return None # use default module creation semantics

    def exec_module(self, module):
        with open(self.filename) as f:
            data = f.read() + "\na=1"

        exec(data, vars(module))

sys.meta_path.insert(0, MyMetaFinder())