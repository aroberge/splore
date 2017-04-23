''' A custom Importer making use of the import hook capability

https://www.python.org/dev/peps/pep-0302/

When a module is imported, it simply adds a line to its source code 
prior to execution.
'''

# imp is deprecated but I wasn't (yet) able to figure out how to use
# its replacement, importlib, to accomplish all that is needed here.

import imp
import sys

class ExperimentalImporter(object):
    '''According to PEP 302, an importer only needs two methods:
       find_module and load_module.
    '''

    def find_module(self, name, path=None):
        '''We don't need anything special here, so we just use the standard
           module finder which, if successful,
           returns a 3-element tuple (file, pathname, description).
           See https://docs.python.org/3/library/imp.html for details
        '''
        self.module_info = imp.find_module(name)
        return self

    def load_module(self, name):
        '''Load a module, given information returned by find_module().
        '''
        if name in sys.modules:
            return sys.modules[name]

        path = self.module_info[1]  # see find_module docstring above

        # How to do the following with importlib ?
        try:
            with open(path) as source_file:
                source = source_file.read() + "\na = 42"
            module = imp.new_module(name)
            sys.modules[name] = module
            exec(source, module.__dict__)
        except Exception as e:
            print("Module %s: exception raised in load_module: %s" % 
                                                   (name, e.__class__.__name__))
            module = imp.load_module(name, *self.module_info)

        return module

sys.meta_path.insert(0, ExperimentalImporter())
