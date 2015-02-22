;; scoppe test
(define pi 3)
(define mul_pi (lambda (x) (begin
    (load-py (quote math))  ;; should redifine pi to its correct value
    (* x pi)
    )))
;; (mul_pi 1 pi)  should use correct value of pi
;; (* 1 pi)   should give 3
