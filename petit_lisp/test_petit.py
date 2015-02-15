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
        version = int(sys.argv[1][1:])
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

    @unittest.skipIf(version == 0, 'multiple args for sum')
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

    @unittest.skipIf(version == 0, 'multiple args for sum')
    def test_add_many(self):
        self.assertEqual(12, pl.evaluate(pl.parse("(+ 3 4 5)")))

    @unittest.skipIf(0 < version < 2, '')
    def test_mul(self):
        self.assertEqual(12, pl.evaluate(pl.parse("(* 3 4)")))
        self.assertEqual(2.4, pl.evaluate(pl.parse("(* 0.6 4)")))

    @unittest.skipIf(version < 2, 'multiple args for mul')
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


if __name__ == '__main__':
    unittest.main()
