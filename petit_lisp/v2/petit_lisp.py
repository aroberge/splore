'''Second version.

   * Handles more mathematical operations, but only with two arguments.
   * Provides nicer way to exit.
   * More robust input handling.

'''

import operator


def my_sum(*args):
    '''sum a list of arguments'''
    return sum(arg for arg in args)


def my_prod(*args):
    '''multiply a list of arguments'''
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
    'exit': exit,
    'quit': exit
}


def evaluate(expr):
    procedure = expr.pop(0)
    return global_env[procedure](*expr)


def parse(s):
    "Parse a Lisp expression from a string."
    return convert_to_list(tokenize(s))


def convert_to_list(tokens):
    "Converts a sequence of tokens into a list"
    tokens.pop(0)  # pop off '('
    return [atomize(token) for token in tokens if token != ")"]


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


def repl():
    "A read-eval-print loop."
    while True:
        inp = read_expression()
        val = evaluate(parse(inp))
        print(val)

if __name__ == '__main__':
    repl()
