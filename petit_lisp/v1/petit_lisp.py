
global_env = {'+': sum}


def evaluate(expr):
    procedure = expr.pop(0)
    return global_env[procedure](expr)


def parse(s):
    "Parse a Lisp expression from a string."
    return convert_to_list(tokenize(s))


def convert_to_list(tokens):
    "Converts a sequence of tokens into a list"
    tokens.pop(0)  # pop off '('
    return [atomize(token) for token in tokens if token != ")"]


def atomize(token):
    "converts token to integers if possible"
    try:
        return int(token)
    except ValueError:
        return token


def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace("(", " ( ").replace(")", " ) ").split()


def read_expression():
    '''Reads an expression from a prompt'''
    return input('repl> ')


def repl():
    "A read-eval-print loop."
    while True:
        inp = read_expression()
        val = evaluate(parse(inp))
        print(val)

if __name__ == '__main__':
    repl()
