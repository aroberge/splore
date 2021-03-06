'''Fourth version.

   * (Re-) Defining variables
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


global_env = {
    '+': my_sum,
    '-': operator.sub,
    '*': my_prod,
    '/': operator.truediv,
    '//': operator.floordiv,
    'quit': exit
}


def evaluate(x):
    "Evaluate an expression in the global environment."
    if isinstance(x, str):            # variable reference
        return global_env[x]
    elif not isinstance(x, list):     # constant literal
        return x
    elif x[0] == 'define':            # (define var exp)
        (_, var, exp) = x
        global_env[var] = evaluate(exp)
    elif x[0] == 'set!':              # (set! var exp)
        (_, var, exp) = x
        global_env[var] = evaluate(exp)
    else:                             # ("procedure" exp*)
        exps = [evaluate(exp) for exp in x]
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
            print(val)
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting petit_lisp\n")
            exit()
        except:
            handle_error()

if __name__ == '__main__':
    repl()
