'''version 9

   * Add ability to load files from repl
   * Add ability to load Python modules
   * Remove imported math module (less "noise") when using (help)
   * Implemented (quote exp)
   * Implemented (begin exp*)

(define sqrt (lambda (x) (begin (load-python (quote math)) (sqrt x))))

'''

import importlib
import operator
import traceback
import pprint
import sys

REPL_STARTED = False


def my_sum(*args):
    '''Sums a list of arguments'''
    return sum(arg for arg in args)


def my_prod(*args):
    '''Multiplies a list of arguments'''
    ans = 1
    for arg in args:
        ans *= arg
    return ans


def my_sub(a, b=None):
    '''Subraction or negation: (- a b) returns a-b; (- a) returns -a'''
    if b is None:
        return -a
    else:
        return a - b


def show_variables(env):
    '''Inspired by Python's help: shows a list of defined names and
       their values or description
    '''
    print()
    names = sorted(env.keys())
    for var in names:
        if var.startswith('__'):
            continue
        val = env[var]
        if hasattr(val, '__doc__') and not isinstance(val, (int, float, str)):
            val = ' '.join(val.__doc__.split('\n')[:3])
        if isinstance(val, str):
            if len(val) > 75:
                val = val[:75] + "..."
        print("  {}: {}\n".format(var, val))
exit.__doc__ = "Quits the repl."


def load_python(module, env):
    '''Loads a Python module in a given environment'''
    mod = importlib.import_module(module)
    env.update(vars(mod))


def load(filename):
    """Execute a program in filename, and start the repl if not already running.
    If an error occurs, execution stops, and we are left in the repl.
    """
    print("\n ==> Loading and executing {}\n".format(filename))

    with open(filename, "r") as f:
        program = f.readlines()
    rps = running_paren_sums(program)
    full_line = ""
    for ((linenumber, paren_sum), program_line) in zip(rps, program):
        if ";" in program_line:
            program_line = program_line.split(";")[0]
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
    if not REPL_STARTED:
        repl()


def common_env(env):
    "Add some built-in procedures and variables to the environment."
    env = Env()
    env.update({
        '+': my_sum,
        '-': my_sub,
        '*': my_prod,
        '/': operator.truediv,
        '//': operator.floordiv,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq,
        'quit': exit,
        '#t': True,
        '#f': False,
        'not': operator.not_,
        'else': True,    # used in cond
        'load': load
    })

    # The following will not be used as it will be intercepted by
    # the same defined inside evaluate; however, by including it here,
    # we make it available to the (help) facility

    env.update({
        'load-python': load_python
    })
    return env


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

global_env = common_env(Env())


def evaluate(x, env=global_env):
    "Evaluate an expression in the global environment."
    if isinstance(x, str):            # variable reference
        return env.find(x)[x]
    elif not isinstance(x, list):     # constant literal
        return x
    elif x[0] == 'quote':             # (quote exp), or (q exp)
        (_, exp) = x
        return exp
    elif x[0] == 'begin':             # (begin exp*)
        for exp in x[1:]:
            val = evaluate(exp, env)
        return val
    elif x[0] == 'define':            # (define var exp)
        (_, var, exp) = x
        env[var] = evaluate(exp, env)
    elif x[0] == 'set!':              # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = evaluate(exp, env)
    elif x[0] == 'lambda':            # (lambda (params*) body)
        (_, params, body) = x
        return Procedure(params, body, env)
    elif x[0] == 'cond':              # (cond (p1 e1) ... (pn en))
        for (p, e) in x[1:]:
            if evaluate(p, env):
                return evaluate(e, env)
    elif x[0] == 'if':                # (if test if_true other)
        (_, test, if_true, other) = x
        return evaluate((if_true if evaluate(test, env) else other), env)
    elif x[0] == 'help':              # (help)
        show_variables(env)
    elif x[0] == 'load-python':
        load_python(evaluate(x[1], env), env)
    else:                             # ("procedure" exp*)
        exps = [evaluate(exp, env) for exp in x]
        procedure = exps.pop(0)
        return procedure(*exps)


def parse(s):
    "Parse a Lisp expression from a string."
    return convert_to_list(tokenize(s))


def convert_to_list(tokens):
    "Converts a sequence of tokens into a list"
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        lst = []
        while tokens[0] != ')':
            lst.append(convert_to_list(tokens))
        tokens.pop(0)   # pop off ')'
        return lst
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atomize(token)


def atomize(token):
    "Converts individual tokens to numbers if possible"
    for conversion in [int, float]:
        try:
            return conversion(token)
        except ValueError:
            pass
    return token


def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace("(", " ( ").replace(")", " ) ").split()


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
    Simple error handling.
    """

    print("an error occurred. Here's the Python traceback:\n")
    traceback.print_exc()
    print()


def repl():
    "A read-eval-print loop."
    global REPL_STARTED
    REPL_STARTED = True

    print("\n  ====  Enter (quit) to end.  ====\n")
    while True:
        inp = read_expression()
        if not inp:
            continue

        try:
            val = evaluate(parse(inp))
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting petit_lisp\n")
            exit()
        except:
            handle_error()
            continue

        if val is not None:
            print(val)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        repl()
