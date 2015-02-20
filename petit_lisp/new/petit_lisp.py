'''New class based version
'''

import importlib
import operator
import traceback
import sys


exit.__doc__ = "Quits the repl."


def load_python(module, env):
    '''Loads a Python module in a given environment'''
    mod = importlib.import_module(module)
    env.update(vars(mod))


def from_python_load(module, env, names=None):
    mod = importlib.import_module(module)
    for name in names:
        env.update({name: getattr(mod, name)})


def from_python_load_as(module, env, names=None):
    mod = importlib.import_module(module)
    name, name_as = names
    env.update({name_as: getattr(mod, name)})


def load(filename):
    """Execute a program in filename, and start the repl if not already running.
    If an error occurs, execution stops, and we are left in the repl.
    """
    print("    --> Loading and executing {}".format(filename))

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
            except Exception as e:
                print("\n    An error occured in loading {}:".format(filename))
                print("line {}:\n{}".format(linenumber, full_line))
                print('      {}: {}'.format(type(e).__name__, e))
                break
            full_line = ""


def common_env(env):
    "Add some built-in procedures and variables to the environment."
    env = Env()
    env.update({
        # '+': my_sum,
        # '-': my_sub,
        # '*': my_prod,
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
        'load': load,
        '#debug': False,
        'nil': []
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
    def __init__(self, params, body, env, opt_param=False):
        self.params, self.body, self.env = params, body, env
        self.opt_param = opt_param

    def __call__(self, *args):
        if self.opt_param:
            args = self.pack_args(args)
        return evaluate(self.body, Env(self.params, args, self.env))

    def pack_args(self, args):
        '''ensures that any extra arguments are packed into a list'''
        if ((len(args) > self.opt_param + 1) or
                (not isinstance(args[self.opt_param], list))):
            newargs = [arg for arg in args[:self.opt_param]]
            newargs.append(list(args[self.opt_param:]))
            return tuple(newargs)
        else:
            return args


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
    "Evaluate an expression in an environment."
    if isinstance(x, str):            # variable reference
        return env.find(x)[x]
    elif not isinstance(x, list):     # constant literal
        return x

    first = x[0]
    if first == 'quote':              # (quote exp), or (q exp)
        (_, exp) = x
        return exp
    elif first == 'begin':            # (begin exp*)
        for exp in x[1:]:
            val = evaluate(exp, env)
        return val
    elif first == 'atom?':            # (atom? exp)
        (_, exp) = x
        return not isinstance(evaluate(exp, env), list)
    elif first == 'eq?':              # (eq? exp1 exp2)
        (_, exp1, exp2) = x
        v1, v2 = evaluate(exp1, env), evaluate(exp2, env)
        return (not isinstance(v1, list)) and (v1 == v2)
    elif first == 'car':               # (car exp)
        (_, exp) = x
        return evaluate(exp, env)[0]
    elif first == 'cdr':               # (cdr exp)
        (_, exp) = x
        return evaluate(exp, env)[1:]
    elif first == 'cons':              # (cons exp1 exp2)
        (_, exp1, exp2) = x
        _x = evaluate(exp2, env)
        if not isinstance(_x, list):
            _x = [_x]
        return [evaluate(exp1, env)] + _x
    elif first == 'define':            # (define var exp)
        (_, var, exp) = x
        env[var] = evaluate(exp, env)
    elif first == 'set!':              # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = evaluate(exp, env)
    elif first == 'lambda':            # (lambda (params*) body)
        (_, params, body) = x
        opt_param = False
        if '.' in params:
            opt_param = params.index('.')
            params.pop(opt_param)
        return Procedure(params, body, env, opt_param)
    elif first == 'cond':              # (cond (p1 e1) ... (pn en))
        for (p, e) in x[1:]:
            if evaluate(p, env):
                return evaluate(e, env)
    elif first == 'if':                # (if test if_true other)
        (_, test, if_true, other) = x
        return evaluate((if_true if evaluate(test, env) else other), env)
    elif first == 'null?':             # (null? exp)
        (_, exp) = x
        return evaluate(exp, env) == []
    elif first == 'load-python':
        load_python(evaluate(x[1], env), env)
    elif first == 'from-python-load':
        from_python_load(evaluate(x[1], env), env, names=[evaluate(arg, env) for arg in x[2:]])
    elif first == 'from-python-load-as':
        from_python_load_as(evaluate(x[1], env), env, names=[evaluate(arg, env) for arg in x[2:]])
    elif first == 'with':   # (with a ...)
        instance = evaluate(x[1], env)
        if hasattr(instance, x[2]):
            attr = getattr(instance, x[2])  # attr = a.b
            if callable(attr):
                exps = [evaluate(exp, env) for exp in x[3:]]
                return attr(*exps)          # a.b(c, d, ...)
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
        raise SyntaxError('convert_to_list: unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        lst = []
        while tokens[0] != ')':
            lst.append(convert_to_list(tokens))
        tokens.pop(0)   # pop off ')'
        return lst
    elif ')' == token:
        raise SyntaxError('convert_to_list: unexpected )')
    elif "'" == token:
        return ['quote', convert_to_list(tokens)]
    else:
        return atomize(token)


def atomize(token):
    "Converts individual tokens to numbers if possible"
    for conversion in [int, float, complex]:
        try:
            return conversion(token.replace('i', 'j'))   # Python uses j instead
        except ValueError:                               # of i for sqrt(-1)
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


class InteractiveInterpreter:
    '''A simple interpreter with built-in help'''
    def __init__(self):
        self.started = False
        self.prompt = 'repl> '
        self.prompt2 = ' ... '

    def repl(self):
        "A read-eval-print loop."
        self.started = True
        print("\n  ====  Enter (quit) to end.  ====\n")
        while True:
            inp = self.read_expression()
            if not inp:
                continue
            try:
                val = evaluate(parse(inp))
                if val is not None:
                    print(self.to_string(val))
            except (KeyboardInterrupt, SystemExit):
                print("\n   Goodbye!")
                return
            except Exception as e:
                print('      {}: {}'.format(type(e).__name__, e))
                if global_env["#debug"]:
                    traceback.print_exc()

    def read_expression(self):
        '''Reads an expression from a prompt'''
        inp = input(self.prompt)
        open_parens = inp.count("(") - inp.count(")")
        while open_parens > 0:
            inp += ' ' + input(self.prompt2)
            open_parens = inp.count("(") - inp.count(")")

        if inp.startswith(("parse", "help", "dir")):
            self.handle_internally(inp)
            return None
        return inp

    def handle_internally(self, inp):
        if inp.startswith("parse "):
            expr = inp[6:]
            print("     {}\n".format(parse(expr)))
        elif inp.startswith("help"):
            help = inp.split()
            if len(help) == 1:
                self.show_variables()
            else:
                self.show_variables(help[1])
        elif inp.startswith("dir"):
            print("\n{}\n".format([x for x in global_env.keys()
                                    if not x.startswith("__")]))

    def start(self):
        '''starts the interpreter if not already running'''
        if self.started:
            return
        try:
            self.repl()
        except BaseException:
            # do not use print after KeyboardInterrupt
            raise
            sys.stdout.write("\n      Exiting petit_lisp.")

    def to_string(self, exp):
        "Convert a Python object back into a Lisp-readable string."
        if not isinstance(exp, list):
            if exp is True:
                return "#t"
            elif exp is False:
                return "#f"
            elif isinstance(exp, complex):
                return str(exp).replace('j', 'i')[1:-1]  # remove () put by Python
            return str(exp)
        else:
            return '(' + ' '.join(self.to_string(s) for s in exp) + ')'

    def show_value(self, var, env):
        '''Displays the value of a variable in a given environment or dict'''
        val = env[var]
        if not isinstance(val, (int, float, complex, str)):
            if hasattr(val, '__doc__') and val.__doc__ is not None:
                val = ' '.join(val.__doc__.split('\n')[:3])
        if isinstance(val, str):
            if len(val) > 75:
                val = val[:75].strip() + "..."
        print("  {}: {}".format(var, val))

    def show_variables(self, obj=None):
        '''Inspired by Python's help: shows a list of defined names and
           their values or description
        '''
        env = global_env
        if obj == "help":
            print("Usage:  help, help variable, help globals, "
                   "help user-defined")
        elif obj not in [None, "user-defined", "globals"]:
            if obj not in env:
                print("Unknown variable: ", obj)
            else:
                self.show_value(obj, env)
        else:
            names = sorted(env.keys())
            for var in names:
                if var.startswith('__'):
                    continue
                if obj == "user-defined" and var in common_env(Env()):
                    continue
                elif obj == "globals" and var not in common_env(Env()):
                    continue
                self.show_value(var, env)
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        load("default_language.lisp")
    interpreter = InteractiveInterpreter()
    interpreter.start()
