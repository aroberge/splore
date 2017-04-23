`import_hook_imp.py` is a custom hook importer. When a module is loaded, its source code is modified so as to add the following line of code:

    a = 42

`test_import.py` is a test file that contains a single print statement, and no declared variable. By importing it using the custom hook importer, we can see how
the value of the variable has been added, confirming that the custom import hook works properly.

    $ python -i import_hook_imp.py
    >>> import test_import
    Check the value of the variable 'a' of this module.
    >>> test_import.a
    42

I have attempted to implement something similar using `importlib` intead of `imp` since `imp` is deprecated; however, I have not been able to make it work.
