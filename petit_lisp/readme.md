# Petit Lisp

This is a simple implementation of a list/scheme like language in Python.

It is strongly inspired by Michael Nielsen's tiddlylisp.py
(http://michaelnielsen.org/ddi/lisp-as-the-maxwells-equations-of-software/)
itself based on Peter Norvig's lispy (http://norvig.com/lispy.html).

The implementation is done in multiple steps, each living in its individual folder.

Version 1
---------

Version 1 implements the basic structure to evaluate
expressions like (+ 3 4), i.e. adding integer values.
 It sets up a simple read-eval-print loop.

Unlike Nielsen's version, the number of numbers that can be added
is not limited to 2.

Unit tests are provided to confirm the proper parsing of expressions
like (+ 3 4 5) which are converted into a list of tokens.
The evaluation of the resulting "abstract syntax tree" is also tested.

The patch decorator from the mock module is used to simulate single entry to Python's input().

Version 2
---------

Version 2 handles more mathematical operations (+, -, *, /, //) and provides also a nicer way to exit the read-eval-print loop --
the previous version required an interrupt using ctrl-c.

Input does not required to be entered all on one line: a continuation
prompt is provided if an expression is deemed incomplete - similar
to what is done with Python.  A different usage of the patch
decorator is needed for unit tests.

A special "hook" is introduced to enable seeing the result
of parsing an expression using the repl for exploration.

Floating point numbers are handled as well as integers.

Version 3
---------

Version 3 allows for nested operations, such as (+ (* 1 2) (- 3 4));
it also has more robust error handling for invalid input.

Version 4
---------

Version 4 allows to define and redefine variables.

Version 5
---------

Version 5 introduces lambda and the concept of scope.

Version 6
---------

Version 6 allows input to be done from a file instead of just
from the input prompt.
