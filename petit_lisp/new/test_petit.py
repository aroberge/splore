''' usage: python test_petit.py
'''
import mock
import unittest
import petit_lisp as pl

pl.evaluate(pl.parse("(load 'default_language.lisp)"))


class TestRead(unittest.TestCase):
    '''Ensures that we handle user input correctly'''

    @mock.patch('builtins.input', return_value="(a b c)")
    def test_get_expr_all_at_once(self, input):
        repl = pl.InteractiveInterpreter()
        self.assertEqual("(a b c)", repl.read_expression())

    @mock.patch('builtins.input', side_effect=['(a', 'b', 'c)'])
    def test_get_expr_in_parts(self, input):
        repl = pl.InteractiveInterpreter()
        self.assertEqual("(a b c)", repl.read_expression())


class TestParse(unittest.TestCase):
    '''Ensures that we parse expressions correctly, transforming them into
       the appropriate "list of lists" representation'''

    def test_parse_add(self):
        self.assertEqual(['+', 3, 4], pl.parse("(+ 3 4)"), msg="basic")
        self.assertEqual(['+', 3, 4], pl.parse(" ( + 3  4  ) "), msg="extra spaces")

    def test_parse_add_more(self):
        self.assertEqual(['+', 3, 4, 5], pl.parse(" ( + 3 4 5)"), msg="more args")

    def test_parse_two_levels(self):
        self.assertEqual(['*', ['+', 3, 4], ['-', 2, 1]], pl.parse(" (* ( + 3 4) (- 2 1))"))


class TestEvaluate(unittest.TestCase):
    '''Evaluate expressions, using the parse function as a first step'''
    def test_add(self):
        self.assertEqual(7, pl.evaluate(pl.parse("(+ 3 4)")))

    def test_add_floats(self):
        self.assertEqual(7.75, pl.evaluate(pl.parse("(+ 3.25 4.5)")))

    def test_sub(self):
        self.assertEqual(1, pl.evaluate(pl.parse("(- 4 3)")))
        self.assertEqual(-1, pl.evaluate(pl.parse("(- 3 4)")))

    def test_add_many(self):
        self.assertEqual(12, pl.evaluate(pl.parse("(+ 3 4 5)")))

    def test_mul(self):
        self.assertEqual(12, pl.evaluate(pl.parse("(* 3 4)")))
        self.assertEqual(2.4, pl.evaluate(pl.parse("(* 0.6 4)")))

    def test_mul_many(self):
        self.assertEqual(60, pl.evaluate(pl.parse("(* 3 4 5)")))

    def test_div(self):
        self.assertEqual(2.0, pl.evaluate(pl.parse("(/ 8 4)")))

    def test_floor_div(self):
        self.assertEqual(2, pl.evaluate(pl.parse("(// 8 4)")))
        self.assertEqual(2, pl.evaluate(pl.parse("(// 9.1 4)")))

    def test_parse_two_levels(self):
        self.assertEqual(13, pl.evaluate(pl.parse(" (+ (* 3 4) (- 2 1))")))

    def test_parse_three_levels(self):
        self.assertEqual(6, pl.evaluate(pl.parse("(// (+ (* 3 4) (- 2 1)) 2)")))

    def test_define(self):
        self.assertEqual(None, pl.evaluate(pl.parse("(define x 3)")))
        self.assertEqual(7, pl.evaluate(pl.parse("(+ x 4)")))
        self.assertEqual(3, pl.evaluate(pl.parse("x")))

    def test_set(self):
        self.assertEqual(None, pl.evaluate(pl.parse("(define x 3)")))
        self.assertEqual(3, pl.evaluate(pl.parse("x")))
        self.assertEqual(None, pl.evaluate(pl.parse("(set! x 4)")))
        self.assertEqual(8, pl.evaluate(pl.parse("(+ x 4)")))

    def test_lambda(self):
        self.assertEqual(None, pl.evaluate(pl.parse("(define square (lambda (x) (* x x)))")))
        self.assertEqual(9, pl.evaluate(pl.parse("(square 3)")))

    def test_load_file(self):
        pl.FileLoader("../define_variable_test.lisp")
        self.assertEqual(3, pl.evaluate(pl.parse("x")))

    def test_load_file_with_comments(self):
        pl.FileLoader("../comments_test.lisp")
        self.assertEqual(49, pl.evaluate(pl.parse("(square 7)")))

    def test_sqrt(self):
        # verify that math functions are loaded properly; only need to verify one
        self.assertEqual(4.0, pl.evaluate(pl.parse("(sqrt 16)")))

    def test_load_python(self):
        # verify that Python module can be imported properly
        pl.evaluate(pl.parse('(load-py (quote math))'))
        self.assertEqual(4.0, pl.evaluate(pl.parse("(sqrt 16)")))

    def test_load_python_scope(self):
        pl.FileLoader("scope_test.lisp")
        self.assertEqual(3, pl.evaluate(pl.parse("(* 1 pi)")))
        from math import pi
        self.assertEqual(pi, pl.evaluate(pl.parse("(mul_pi 1)")))


class TestLogic(unittest.TestCase):

    def test_if(self):
        # test "if", "#t", "#f"
        pl.evaluate(pl.parse("(if #t (define x 1) (define x 2))"))
        self.assertEqual(1, pl.evaluate(pl.parse("x")))
        pl.evaluate(pl.parse("(if #f (define x 3) (define x 4))"))
        self.assertEqual(4, pl.evaluate(pl.parse("x")))

    def test_not(self):
        # test "if", "#t", "#f"
        pl.evaluate(pl.parse("(if (not #t) (define x 1) (define x 2))"))
        self.assertEqual(2, pl.evaluate(pl.parse("x")))
        pl.evaluate(pl.parse("(if (not #f) (define x 3) (define x 4))"))
        self.assertEqual(3, pl.evaluate(pl.parse("x")))

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

    def test_cons(self):
        expr = "(define a (cons 1 (cons 2 (cons 3 (cons 4 '())))))"
        expr2 = "'(1 2 3 4)"
        pl.evaluate(pl.parse(expr))
        self.assertEqual(pl.evaluate(pl.parse(expr2)), pl.evaluate(pl.parse("a")))

    def test_car(self):
        expr = "(define a (cons 1 (cons 2 (cons 3 (cons 4 '())))))"
        expr2 = "(car a)"
        pl.evaluate(pl.parse(expr))
        self.assertEqual(1, pl.evaluate(pl.parse(expr2)))

    def test_cdr(self):
        expr = "(define a (cons 1 (cons 2 (cons 3 (cons 4 '())))))"
        expr2 = "(cdr a)"
        pl.evaluate(pl.parse(expr))
        self.assertEqual(pl.evaluate(pl.parse("'(2 3 4)")), pl.evaluate(pl.parse(expr2)))

if __name__ == '__main__':
    unittest.main()
