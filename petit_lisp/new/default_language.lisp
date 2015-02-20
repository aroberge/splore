(load-python 'my_math)
(define + my_sum)
(define * my_prod)
(define - my_sub)
(define last (lambda (y) (cond ( (null? (cdr y)) (car y)) (else (last (cdr y))))))
(define append (lambda (x y)
    (cond ( (null? x) y)
        (else (cons (car x) (append (cdr x) y))))))
(define list (lambda (x . y) (append (cons x '()) y)))
(define add (lambda (x y . z)
    (cond ((null? z) (+ x y))
          (else (add (+ x y) (car z) (cdr z))))
    ))