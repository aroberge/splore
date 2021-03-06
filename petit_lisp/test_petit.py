''' usage: python test_petit.py [v?]

optional argument: v?  where ? is a number will use the  petit_lisp.py version
                   located in v?/petit_lisp.py  otherwise the default (final)
                   version will be used.
'''
import mock
import unittest

if __name__ == '__main__':
    import sys
    import os
    if len(sys.argv) > 1 and sys.argv[1].startswith('v'):
        sys.path.insert(0, os.path.join(os.getcwd(), sys.argv[1]))
        try:
            version = int(sys.argv[1][1:])
        except ValueError:
            version = float(sys.argv[1][1:])
        sys.argv.pop(1)
        import petit_lisp as pl
    else:
        version = 0
        import petit_lisp as pl

# Since we focus on a read-eval-print loop version, we only test the main
# parts of the interpreter  ("read", "parse", "eval") and do not
# test the helper functions, which leaves us with the flexibility to
# change them as the design evolves and still have non-failing tests
# for all versions.


class TestRead(unittest.TestCase):
    '''Ensures that we handle user input correctly'''

    @mock.patch('builtins.input', return_value="(a b c)")
    def test_get_expr_all_at_once(self, input):
        self.assertEqual("(a b c)", pl.read_expression())

    @unittest.skipIf(0 < version < 2, '')
    @mock.patch('builtins.input', side_effect=['(a', 'b', 'c)'])
    def test_get_expr_in_parts(self, input):
        self.assertEqual("(a b c)", pl.read_expression())


class TestParse(unittest.TestCase):
    '''Ensures that we parse expressions correctly, transforming them into
       the appropriate "list of lists" representation'''

    def test_parse_add(self):
        self.assertEqual(['+', 3, 4], pl.parse("(+ 3 4)"), msg="basic")
        self.assertEqual(['+', 3, 4], pl.parse(" ( + 3  4  ) "), msg="extra spaces")

    def test_parse_add_more(self):
        self.assertEqual(['+', 3, 4, 5], pl.parse(" ( + 3 4 5)"), msg="more args")

    @unittest.skipIf(0 < version < 3, '')
    def test_parse_two_levels(self):
        self.assertEqual(['*', ['+', 3, 4], ['-', 2, 1]], pl.parse(" (* ( + 3 4) (- 2 1))"))


class TestEvaluate(unittest.TestCase):
    '''Evaluate expressions, using the parse function as a first step'''
    def test_add(self):
        self.assertEqual(7, pl.evaluate(pl.parse("(+ 3 4)")))

    @unittest.skipIf(0 < version < 2, '')
    def test_add_floats(self):
        self.assertEqual(7.75, pl.evaluate(pl.parse("(+ 3.25 4.5)")))

    @unittest.skipIf(0 < version < 2, '')
    def test_sub(self):
        self.assertEqual(1, pl.evaluate(pl.parse("(- 4 3)")))
        self.assertEqual(-1, pl.evaluate(pl.parse("(- 3 4)")))

    def test_add_many(self):
        self.assertEqual(12, pl.evaluate(pl.parse("(+ 3 4 5)")))

    @unittest.skipIf(0 < version < 2, '')
    def test_mul(self):
        self.assertEqual(12, pl.evaluate(pl.parse("(* 3 4)")))
        self.assertEqual(2.4, pl.evaluate(pl.parse("(* 0.6 4)")))

    @unittest.skipIf(0 < version < 2, 'multiple args for mul')
    def test_mul_many(self):
        self.assertEqual(60, pl.evaluate(pl.parse("(* 3 4 5)")))

    @unittest.skipIf(0 < version < 2, '')
    def test_div(self):
        self.assertEqual(2.0, pl.evaluate(pl.parse("(/ 8 4)")))

    @unittest.skipIf(0 < version < 2, '')
    def test_floor_div(self):
        self.assertEqual(2, pl.evaluate(pl.parse("(// 8 4)")))
        self.assertEqual(2, pl.evaluate(pl.parse("(// 9.1 4)")))

    @unittest.skipIf(0 < version < 3, '')
    def test_parse_two_levels(self):
        self.assertEqual(13, pl.evaluate(pl.parse(" (+ (* 3 4) (- 2 1))")))

    @unittest.skipIf(0 < version < 3, '')
    def test_parse_three_levels(self):
        self.assertEqual(6, pl.evaluate(pl.parse("(// (+ (* 3 4) (- 2 1)) 2)")))

    @unittest.skipIf(0 < version < 4, '')
    def test_define(self):
        self.assertEqual(None, pl.evaluate(pl.parse("(define x 3)")))
        self.assertEqual(7, pl.evaluate(pl.parse("(+ x 4)")))
        self.assertEqual(3, pl.evaluate(pl.parse("x")))

    @unittest.skipIf(0 < version < 4, '')
    def test_set(self):
        self.assertEqual(None, pl.evaluate(pl.parse("(define x 3)")))
        self.assertEqual(3, pl.evaluate(pl.parse("x")))
        self.assertEqual(None, pl.evaluate(pl.parse("(set! x 4)")))
        self.assertEqual(8, pl.evaluate(pl.parse("(+ x 4)")))

    @unittest.skipIf(0 < version < 5, '')
    def test_lambda(self):
        self.assertEqual(None, pl.evaluate(pl.parse("(define square (lambda (x) (* x x)))")))
        self.assertEqual(9, pl.evaluate(pl.parse("(square 3)")))

    @unittest.skipIf(0 < version < 6, '')
    def test_load_file(self):
        pl.REPL_STARTED = True
        self.assertEqual(None, pl.load("define_variable_test.lisp"))
        self.assertEqual(3, pl.evaluate(pl.parse("x")))

    @unittest.skipIf(0 < version < 7, '')
    def test_load_file_with_comments(self):
        pl.REPL_STARTED = True
        self.assertEqual(None, pl.load("comments_test.lisp"))
        self.assertEqual(49, pl.evaluate(pl.parse("(square 7)")))

    @unittest.skipIf(version not in [0, 7, 8], '')
    def test_sqrt(self):
        # verify that math functions are loaded properly; only need to verify one
        self.assertEqual(4.0, pl.evaluate(pl.parse("(sqrt 16)")))

    @unittest.skipIf(0 < version < 9, '')
    def test_load_python(self):
        # verify that Python module can be imported properly
        pl.evaluate(pl.parse('(load-python (quote math))'))
        self.assertEqual(4.0, pl.evaluate(pl.parse("(sqrt 16)")))

    @unittest.skipIf(0 < version < 9, '')
    def test_load_python_scope(self):
        pl.REPL_STARTED = True
        pl.load("scope_test.lisp")
        self.assertEqual(3, pl.evaluate(pl.parse("(* 1 pi)")))
        from math import pi
        self.assertEqual(pi, pl.evaluate(pl.parse("(mul_pi 1)")))


class TestLogic(unittest.TestCase):

    @unittest.skipIf(0 < version < 8, '')
    def test_if(self):
        # test "if", "#t", "#f"
        pl.evaluate(pl.parse("(if #t (define x 1) (define x 2))"))
        self.assertEqual(1, pl.evaluate(pl.parse("x")))
        self.assertEqual(None, pl.evaluate(pl.parse("(if #f (define x 3) (define x 4))")))
        self.assertEqual(4, pl.evaluate(pl.parse("x")))

    @unittest.skipIf(0 < version < 8, '')
    def test_not(self):
        # test "if", "#t", "#f"
        self.assertEqual(None, pl.evaluate(pl.parse("(if (not #t) (define x 1) (define x 2))")))
        self.assertEqual(2, pl.evaluate(pl.parse("x")))
        self.assertEqual(None, pl.evaluate(pl.parse("(if (not #f) (define x 3) (define x 4))")))
        self.assertEqual(3, pl.evaluate(pl.parse("x")))

    @unittest.skipIf(0 < version < 8, '')
    def test_cond(self):
        # test "cond", ">", ">" ,"="
        expr = """
(define abs (lambda (x)
    (cond ((> x 0) x)
          ((= x 0) 0)
          ((< x 0) (- x)))))"""
        self.assertEqual(None, pl.evaluate(pl.parse(expr)))
        self.assertEqual(2, pl.evaluate(pl.parse("(abs 2)")))
        self.assertEqual(3, pl.evaluate(pl.parse("(abs -3)")))
        self.assertEqual(0, pl.evaluate(pl.parse("(abs 0)")))

    @unittest.skipIf(0 < version < 8, '')
    def test_cond_with_else(self):
        # test "cond", "else", "<="
        expr = """
(define abs2 (lambda (x)
    (cond ((<= x 0) (- x))
          (else x)
          )))"""
        self.assertEqual(None, pl.evaluate(pl.parse(expr)))
        self.assertEqual(2, pl.evaluate(pl.parse("(abs2 2)")))
        self.assertEqual(3, pl.evaluate(pl.parse("(abs2 -3)")))
        self.assertEqual(0, pl.evaluate(pl.parse("(abs2 0)")))


class TestLists(unittest.TestCase):

    @unittest.skipIf(0 < version < 11, '')
    def test_cons(self):
        expr = "(define a (cons 1 (cons 2 (cons 3 (cons 4 '())))))"
        expr2 = "'(1 2 3 4)"
        pl.evaluate(pl.parse(expr))
        self.assertEqual(pl.evaluate(pl.parse(expr2)), pl.evaluate(pl.parse("a")))

    @unittest.skipIf(0 < version < 11, '')
    def test_car(self):
        expr = "(define a (cons 1 (cons 2 (cons 3 (cons 4 '())))))"
        expr2 = "(car a)"
        pl.evaluate(pl.parse(expr))
        self.assertEqual(1, pl.evaluate(pl.parse(expr2)))

    @unittest.skipIf(0 < version < 11, '')
    def test_cdr(self):
        expr = "(define a (cons 1 (cons 2 (cons 3 (cons 4 '())))))"
        expr2 = "(cdr a)"
        pl.evaluate(pl.parse(expr))
        self.assertEqual(pl.evaluate(pl.parse("'(2 3 4)")), pl.evaluate(pl.parse(expr2)))

if __name__ == '__main__':
    unittest.main()
