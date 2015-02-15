'''Fourth version.

   * Defining variables
   * Multiple environments/scopes
'''

import operator
import traceback


def my_sum(*args):
    '''sum a list of arguments'''
    return sum(arg for arg in args)


def my_prod(*args):
    '''multiply a list of arguments'''
    ans = 1
    for arg in args:
        ans *= arg
    return ans


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."

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


def add_globals(env):
    "Add some built-in procedures and variables to the environment."
    env.update({
        '+': my_sum,
        '-': operator.sub,
        '*': my_prod,
        '/': operator.truediv,
        '//': operator.floordiv,
        'exit': exit,
        'quit': exit
    })
    return env

global_env = add_globals(Env())


def evaluate(x, env=global_env):
    "Evaluate an expression in the global environment."
    if isinstance(x, str):            # variable reference
        return env.find(x)[x]
    elif not isinstance(x, list):     # constant literal
        return x
    elif x[0] == 'define':            # (define var exp)
        (_, var, exp) = x
        env[var] = evaluate(exp, env)
    elif x[0] == 'set!':            # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = evaluate(exp, env)
    elif x[0] == 'lambda':          # (lambda (var*) exp)
        (_, vars, exp) = x
        return lambda *args: evaluate(exp, Env(vars, args, env))
    else:                             # (procedure exp*)
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
    return inp


def handle_error(inp, expr=None, source=None):
    """
    Simple error handling for both the repl and load.
    """
    print("An error occured in {}.\n".format(repr(source)))
    print("The original input was:\n\n{}\n".format(inp))
    if expr is not None:
        print("The expression was:\n\n{}\n".format(expr))

    print("Here's the Python stack trace:\n")
    traceback.print_exc()
    print()


def repl():
    "A read-eval-print loop."
    while True:
        inp = read_expression()

        try:
            expr = parse(inp)
        except:
            handle_error(inp, source="parse")
            continue

        try:
            val = evaluate(expr)
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting petit_lisp\n")
            exit()
        except:
            handle_error(inp=inp, expr=expr, source="evaluate")
            continue

        if val is not None:
            print(val)

if __name__ == '__main__':
    repl()
