# petit_lisp.py
#
# Starting point: tiddlylisp.py by Michael Nielsen.  See
# http://michaelnielsen.org/ddi/lisp-as-the-maxwells-equations-of-software/
#
# Based on Peter Norvig's lispy (http://norvig.com/lispy.html),
# copyright by Peter Norvig, 2010.
#
# Converted to work with Python 3 and extended
#

import math
import operator
import pprint
import re
import sys
import traceback

Symbol = str


def my_sum(*args):
    '''sum a list of arguments'''
    return sum(arg for arg in args)


def my_prod(*args):
    '''multiply a list of arguments'''
    ans = 1
    for arg in args:
        ans *= arg
    return ans


class Procedure(object):
    "A user-defined procedure."
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env

    def __call__(self, *args):
        return evaluate(self.body, Env(self.params, args, self.env))


class Env(dict):
    "An environment: a dict of {'var': val} pairs, with an outer Env."

    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        if var in self:
            return self
        elif self.outer is not None:
            return self.outer.find(var)
        else:
            raise ValueError("{} is not defined".format(var))


def common_env(env):
    "Add some built-in procedures and variables to the environment."
    env = Env()
    env.update(vars(math))  # sin, cos, sqrt, pi, ...
    env.update(
        {'+': my_sum,
         '-': operator.sub,
         '*': my_prod,
         '/': operator.truediv,
         '>': operator.gt,
         '<': operator.lt,
         '>=': operator.ge,
         '<=': operator.le,
         '=': operator.eq,
         '//': operator.floordiv,
         'exit': exit,
         'quit': exit
         })
    env.update({'True': True, 'False': False})
    return env

global_env = common_env(Env())


def evaluate(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):              # variable reference
        return env.find(x)[x]
    elif not isinstance(x, list):          # constant literal
        return x
    elif x[0] == 'quote' or x[0] == 'q':  # (quote exp), or (q exp)
        (_, exp) = x
        return exp
    elif x[0] == 'atom?':           # (atom? exp)
        (_, exp) = x
        return not isinstance(evaluate(exp, env), list)
    elif x[0] == 'eq?':             # (eq? exp1 exp2)
        (_, exp1, exp2) = x
        v1, v2 = evaluate(exp1, env), evaluate(exp2, env)
        return (not isinstance(v1, list)) and (v1 == v2)
    elif x[0] == 'car':             # (car exp)
        (_, exp) = x
        return evaluate(exp, env)[0]
    elif x[0] == 'cdr':             # (cdr exp)
        (_, exp) = x
        return evaluate(exp, env)[1:]
    elif x[0] == 'cons':            # (cons exp1 exp2)
        (_, exp1, exp2) = x
        return [evaluate(exp1, env)]+evaluate(exp2, env)
    elif x[0] == 'cond':            # (cond (p1 e1) ... (pn en))
        for (p, e) in x[1:]:
            if evaluate(p, env):
                return evaluate(e, env)
    elif x[0] == 'null?':           # (null? exp)
        (_, exp) = x
        return evaluate(exp, env) == []
    elif x[0] == 'if':              # (if test conseq alt)
        (_, test, conseq, alt) = x
        return evaluate((conseq if evaluate(test, env) else alt), env)
    elif x[0] == 'set!':            # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = evaluate(exp, env)
    elif x[0] == 'define':          # (define var exp)
        (_, var, exp) = x
        env[var] = evaluate(exp, env)
    elif x[0] == 'lambda':          # (lambda (var*) exp)
        (_, vars, exp) = x
        return lambda *args: evaluate(exp, Env(vars, args, env))
    elif x[0] == 'begin':           # (begin exp*)
        for exp in x[1:]:
            val = evaluate(exp, env)
        return val
    else:                           # (proc exp*)
        exps = [evaluate(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)


def parse(s):
    "Parse a Lisp expression from a string."
    return read_from(tokenize(s))


def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace("(", " ( ").replace(")", " ) ").split()


def read_from(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        lst = []
        while tokens[0] != ')':
            lst.append(read_from(tokens))
        tokens.pop(0)   # pop off ')'
        return lst
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def to_string(exp):
    "Convert a Python object back into a Lisp-readable string."
    if not isinstance(exp, list):
        return str(exp)
    else:
        return '(' + ' '.join(to_string(s) for s in exp) + ')'


def load(filename, start_repl=True):
    """
    Load the program in filename, execute it, and start the repl.
    If an error occurs, execution stops, and we are left in the repl.
    """
    print("\n ==> Loading and executing {}\n".format(filename))

    with open(filename, "r") as f:
        program = f.readlines()
    rps = running_paren_sums(program)
    full_line = ""
    for ((linenumber, paren_sum), program_line) in zip(rps, program):
        program_line = remove_comments(program_line)
        program_line = program_line.strip()
        full_line += program_line + " "
        if paren_sum == 0 and full_line.strip():
            try:
                val = evaluate(parse(full_line))
                if val is not None:
                    print(val)
            except:
                handle_error()
                print("\nAn error occured on line {}:\n{}".format(linenumber,
                                                                     full_line))
                break
            full_line = ""
    if start_repl:
        repl()


def running_paren_sums(program):
    """
    Map the lines in the list program to a list whose entries contain
    a running sum of the per-line difference between the number of '('
    parentheses and the number of ')' parentheses.
    """
    total = 0
    rps = []
    for linenumber, line in enumerate(program):
        total += line.count("(")-line.count(")")
        rps.append((linenumber, total))
    return rps


def remove_comments(string):
    '''remove comments identified by using a ; as starting character'''
    pattern = '([^"]*(?:\\.[^\\"]*))|(;.*$)'
    # first group captures quoted double strings
    # second group captures comments (;this is a comment)
    regex = re.compile(pattern)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string
    return regex.sub(_replacer, string)


def repl():
    "A prompt-read-eval-print loop."
    while True:
        try:
            inp = read_expression()
            val = evaluate(parse(inp))
            if val is not None:
                print(to_string(val))
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting petit_lisp\n")
            sys.exit()
        except:
            handle_error(inp)


def read_expression():
    '''Reads an expression from a prompt'''
    prompt = 'repl> '
    prompt2 = ' ... '
    inp = input(prompt)
    open_parens = inp.count("(") - inp.count(")")
    while open_parens > 0:
        inp += ' ' + input(prompt2)
        open_parens = inp.count("(") - inp.count(")")
    if inp.startswith("parse "):
        pprint.pprint(parse(inp[6:]))
        return None
    return inp


def handle_error():
    """
    Simple error handling for both the repl and load.
    """
    print("An error occurred.  Here's the Python stack trace:\n")
    traceback.print_exc()
    print("")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        print("\n  ====  Enter (quit) to end.  ====\n")
        repl()
