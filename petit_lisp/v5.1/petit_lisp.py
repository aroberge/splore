'''Version 5.1

    * adding help
'''

import operator
import traceback
import pprint


def my_sum(*args):
    '''Returns the sum of the supplied arguments'''
    return sum(arg for arg in args)


def my_prod(*args):
    '''Returns the product of the supplied arguments'''
    ans = 1
    for arg in args:
        ans *= arg
    return ans


def show_variables(env):
    '''Inspired by Python's help: shows a list of defined names and
       their values or description
    '''
    print()
    for var in env:
        val = env[var]
        if hasattr(val, '__doc__') and not isinstance(val, (int, float, str)):
            val = val.__doc__
        print("  {}: {}\n".format(var, val))
exit.__doc__ = "Quits the repl."


def common_env(env):
    "Add some built-in procedures and variables to the environment."
    env = Env()
    env.update({
        '+': my_sum,
        '-': operator.sub,
        '*': my_prod,
        '/': operator.truediv,
        '//': operator.floordiv,
        'quit': exit
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
    elif x[0] == 'define':            # (define var exp)
        (_, var, exp) = x
        env[var] = evaluate(exp, env)
    elif x[0] == 'set!':              # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = evaluate(exp, env)
    elif x[0] == 'lambda':            # (lambda (params*) body)
        (_, params, body) = x
        return Procedure(params, body, env)
    elif x[0] == 'help':
        show_variables(env)
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

if __name__ == '__main__':
    repl()
