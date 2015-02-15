# Petit Lisp

This is a simple implementation of a list/scheme like language in Python.

It is strongly inspired by Michael Nielsen's tiddlylisp.py
(http://michaelnielsen.org/ddi/lisp-as-the-maxwells-equations-of-software/)
itself based on Peter Norvig's lispy (http://norvig.com/lispy.html).

The implementation is done in multiple steps, each living in its individual folder.

Version 1
---------

Version 1 implements the basic structure to evaluate
expressions like (+ 3 4). It sets up a simple read-eval-print loop.

Unlike Nielsen's version, the number of numbers that can be added
is not limited to 2.

Unit tests are provided to confirm the proper parsing of expressions
like (+ 3 4 5) which are converted into a list of tokens.
The evaluation of the resulting "abstract syntax tree" is also tested.

The patch decorator from the mock module is used to simulate single entry to Python's input().
