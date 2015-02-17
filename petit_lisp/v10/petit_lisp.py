'''version 10

   * Add complex as supported numeric type
     - note that there must not be any spaces and "j" is used to represent
       the imaginary part  as in  z = 3+2j
   * Modified help to allow displaying only user-defined variables.
   * Added (call ...) which is helpful for creating instances of Python classes.
   * Added (with inst attr ...) to call method or attribute of Python instance.
   * Added support for 'x as (quote x)
     - this means we can do (load-python 'math) instead of
       (load-python (quote math))
   * Simplified error handling output (eliminated the traceback)

'''

import importlib
import operator
import traceback
import pprint
import pydoc
import sys

REPL_STARTED = False


def my_sum(*args):
    '''Returns the sum of the supplied arguments'''
    return sum(arg for arg in args)


def my_prod(*args):
    '''Returns the product of the supplied arguments'''
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


def show_value(var, env):
    '''Displays the value of a variable in a given environment or dict'''
    val = env[var]
    if not isinstance(val, (int, float, complex, str)):
        if hasattr(val, '__doc__') and val.__doc__ is not None:
            val = ' '.join(val.__doc__.split('\n')[:3])
    if isinstance(val, str):
        if len(val) > 75:
            val = val[:75].strip() + "..."
    print("  {}: {}".format(var, val))


def show_variables(env, obj=None):
    '''Inspired by Python's help: shows a list of defined names and
       their values or description
    '''
    if obj == "help":
        print("Usage:  (help), (help variable), (help #globals), "
               "(help #user-defined)")
    elif obj not in [None, "#user-defined", "#globals"]:
        if obj not in env:
            print("Unknown variable: ", obj)
        else:
            show_value(obj, env)
    else:
        names = sorted(env.keys())
        for var in names:
            if var.startswith('__'):
                continue
            if obj == "#user-defined" and var in common_env(Env()):
                continue
            elif obj == "#globals" and var not in common_env(Env()):
                continue
            show_value(var, env)
    print()

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
        if len(x) > 1:
            show_variables(env, x[1])
        else:
            show_variables(env)
    elif x[0] == 'python-help':
        if len(x) > 1:
            if var not in env:
                print("Unkown variable", var)
                return
            var = evaluate(x[1], env)
            print("Help for {}: {}".format(x[1], var))
            pydoc.help(var)
        else:
            print("Usage: (python-help variable)")
    elif x[0] == 'load-python':
        load_python(evaluate(x[1], env), env)
    elif x[0] == 'call':   # e.g. (call Class  ....)
        instance = evaluate(x[1], env)
        if callable(instance):
            exps = [evaluate(exp, env) for exp in x[2:]]
            return instance(*exps)
        else:
            print("{} is not callable".format(x[1]))
    elif x[0] == 'with':   # (with a ...)
        instance = evaluate(x[1], env)
        if hasattr(instance, x[2]):
            attr = getattr(instance, x[2])  # attr = a.b
            if callable(attr):
                exps = [evaluate(exp, env) for exp in x[3:]]
                return attr(*exps)            # a.b(c, d, ...)
            else:
                return attr
        else:
            print("{} has no attribute {}.".format(x[1], x[2]))
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
    elif "'" == token:
        return ['quote', convert_to_list(tokens)]
    else:
        return atomize(token)


def atomize(token):
    "Converts individual tokens to numbers if possible"
    for conversion in [int, float, complex]:
        try:
            return conversion(token)
        except ValueError:
            pass
    return token


def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace("(", " ( ").replace(")", " ) ").replace("'", " ' ").split()


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
    print("\n       {}\n ".format(traceback.format_exc().splitlines()[-1]))


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
            if val is not None:
                print(val)
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting petit_lisp\n")
            exit()
        except:
            handle_error()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        repl()
