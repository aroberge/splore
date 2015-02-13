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

import sys
import traceback
import operator

Symbol = str


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."

    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        return self if var in self else self.outer.find(var)


def add_globals(env):
    "Add some built-in procedures and variables to the environment."
    env.update(
        {'+': operator.add,
         '-': operator.sub,
         '*': operator.mul,
         '/': operator.truediv,
         '>': operator.gt,
         '<': operator.lt,
         '>=': operator.ge,
         '<=': operator.le,
         '=': operator.eq
         })
    env.update({'True': True, 'False': False})
    return env

global_env = add_globals(Env())


def eval(x, env=global_env):
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
        return not isinstance(eval(exp, env), list)
    elif x[0] == 'eq?':             # (eq? exp1 exp2)
        (_, exp1, exp2) = x
        v1, v2 = eval(exp1, env), eval(exp2, env)
        return (not isinstance(v1, list)) and (v1 == v2)
    elif x[0] == 'car':             # (car exp)
        (_, exp) = x
        return eval(exp, env)[0]
    elif x[0] == 'cdr':             # (cdr exp)
        (_, exp) = x
        return eval(exp, env)[1:]
    elif x[0] == 'cons':            # (cons exp1 exp2)
        (_, exp1, exp2) = x
        return [eval(exp1, env)]+eval(exp2, env)
    elif x[0] == 'cond':            # (cond (p1 e1) ... (pn en))
        for (p, e) in x[1:]:
            if eval(p, env):
                return eval(e, env)
    elif x[0] == 'null?':           # (null? exp)
        (_, exp) = x
        return eval(exp, env) == []
    elif x[0] == 'if':              # (if test conseq alt)
        (_, test, conseq, alt) = x
        return eval((conseq if eval(test, env) else alt), env)
    elif x[0] == 'set!':            # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'define':          # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'lambda':          # (lambda (var*) exp)
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    elif x[0] == 'begin':           # (begin exp*)
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    else:                           # (proc exp*)
        exps = [eval(exp, env) for exp in x]
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


def load(filename):
    """
    Load the tiddlylisp program in filename, execute it, and start the
    repl.  If an error occurs, execution stops, and we are left in the
    repl.  Note that load copes with multi-line tiddlylisp code by
    merging lines until the number of opening and closing parentheses
    match.
    """
    print("Loading and executing %s" % filename)
    f = open(filename, "r")
    program = f.readlines()
    f.close()
    rps = running_paren_sums(program)
    full_line = ""
    for (paren_sum, program_line) in zip(rps, program):
        program_line = program_line.strip()
        full_line += program_line+" "
        if paren_sum == 0 and full_line.strip() != "":
            try:
                val = eval(parse(full_line))
                if val is not None:
                    print(to_string(val))
            except:
                handle_error()
                print("\nThe line in which the error occurred:\n%s" % full_line)
                break
            full_line = ""
    repl()


def running_paren_sums(program):
    """
    Map the lines in the list program to a list whose entries contain
    a running sum of the per-line difference between the number of '('
    parentheses and the number of ')' parentheses.
    """
    count_open_parens = lambda line: line.count("(")-line.count(")")
    paren_counts = map(count_open_parens, program)
    rps = []
    total = 0
    for paren_count in paren_counts:
        total += paren_count
        rps.append(total)
    return rps


def repl(prompt='repl> '):
    "A prompt-read-eval-print loop."
    prompt2 = "...  "
    while True:
        try:
            inp = input(prompt)
            open_parens = inp.count("(") - inp.count(")")
            while open_parens > 0:
                inp += ' ' + input(prompt2)
                open_parens = inp.count("(") - inp.count(")")
            val = eval(parse(inp))
            if val is not None:
                print(to_string(val))
        except KeyboardInterrupt:
            print("\nExiting tiddlylisp\n")
            sys.exit()
        except:
            handle_error(inp)


def handle_error(inp):
    """
    Simple error handling for both the repl and load.
    """
    if inp.lower() == "quit":
        print("\nGoodbye!")
        sys.exit()
    print("An error occurred.  Here's the Python stack trace:\n")
    traceback.print_exc()
    print("")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        print("\n  ====  Enter 'quit' to end.  ====\n")
        repl()
