''' A custom Importer making use of the import hook capability

https://www.python.org/dev/peps/pep-0302/

When a module is imported, it simply adds a line to its source code 
prior to execution.
'''
print("WARNING: this code does not work.")

import importlib
import sys

class ExperimentalImporter(object):
    '''According to PEP 302, an importer only needs two methods:
       find_module and load_module.
    '''

    def find_module(self, name, path=None):
        '''We don't need anything special here, so we just use the standard
           module finder.
        '''
        self.spec = importlib.util.find_spec(name)
        return self

    def find_spec(self, name, *args):
        '''find_spec apparently needed for custom hook importer using 
        importlib
        '''
        return importlib.util.find_spec(name)


    def load_module(self, name):
        '''Load a module, given information returned by find_module().
        '''
        if name in sys.modules:
            return sys.modules[name]

        source = self.module_spec.loader.get_source(name)
        module = importlib.util.module_from_spec(self.spec)
        sys.modules[name] = module
        new_source = source + "\na=42"
        codeobj = compile(new_source, module.__spec__.origin, 'exec')
        exec(codeobj, module.__dict__)

        return module

sys.meta_path.insert(0, ExperimentalImporter())
