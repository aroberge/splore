def my_sum(*args):
    '''Returns the sum of the supplied arguments'''
    return sum(arg for arg in args)


def my_prod(*args):
    '''Returns the product of the supplied arguments'''
    ans = 1
    for arg in args:
        ans *= arg
    return ans


def my_sub(a, b=None):
    '''Subraction or negation: (- a b) returns a-b; (- a) returns -a'''
    if b is None:
        return -a
    else:
        return a - b
