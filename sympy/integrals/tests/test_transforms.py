from sympy.integrals.transforms import (mellin_transform,
    inverse_mellin_transform, laplace_transform, inverse_laplace_transform)
from sympy import (gamma, exp, oo, Heaviside, symbols, re, factorial, pi,
                   cos, S, And, sin)
from sympy.abc import x, s, a
nu, beta, rho = symbols('nu beta rho')

def test_undefined_function():
    from sympy import Function, MellinTransform
    f = Function('f')
    assert mellin_transform(f(x), x, s) == MellinTransform(f(x), x, s)
    assert mellin_transform(f(x) + exp(-x), x, s) == \
           (MellinTransform(f(x), x, s) + gamma(s), (0, oo), True)

def test_free_symbols():
    from sympy import Function
    f = Function('f')
    assert mellin_transform(f(x), x, s).free_symbols == set([s])
    assert mellin_transform(f(x)*a, x, s).free_symbols == set([s, a])

def test_as_integral():
    from sympy import Function, Integral
    f = Function('f')
    assert mellin_transform(f(x), x, s).rewrite('Integral') == \
           Integral(x**(s - 1)*f(x), (x, 0, oo))

def test_mellin_transform():
    MT = mellin_transform

    # 8.4.2
    assert MT(x**nu*Heaviside(x - 1), x, s) \
           == (1/(-nu - s), (-oo, -re(nu)), True)
    assert MT(x**nu*Heaviside(1 - x), x, s) \
           == (1/(nu + s), (-re(nu), oo), True)

    assert MT((1-x)**(beta - 1)*Heaviside(1-x), x, s) \
           == (gamma(beta)*gamma(s)/gamma(beta + s),
               (0, oo), re(-beta) < 0)
    assert MT((x-1)**(beta - 1)*Heaviside(x-1), x, s) \
           == (gamma(beta)*gamma(1 - beta - s)/gamma(1 - s),
               (-oo, -re(beta) + 1), re(-beta) < 0)

    assert MT((1+x)**(-rho), x, s) == (gamma(s)*gamma(rho-s)/gamma(rho),
                                       (0, re(rho)), True)

    # TODO also the conditions should be simplified
    assert MT(abs(1-x)**(-rho), x, s) == \
        (cos(pi*rho/2 - pi*s)*gamma(s)*gamma(rho-s)/(cos(pi*rho/2)*gamma(rho)),\
         (0, re(rho)), And(re(rho) - 1 < 0, re(rho) < 1))

    mt = MT((1-x)**(beta-1)*Heaviside(1-x)
            + a*(x-1)**(beta-1)*Heaviside(x-1), x, s)
    assert mt[1], mt[2] == ((0, -re(beta) + 1), True)
    # TODO ...

    # 8.4.2
    assert MT(exp(-x), x, s) == (gamma(s), (0, oo), True)
    assert MT(exp(-1/x), x, s) == (gamma(-s), (-oo, 0), True)

def test_inverse_mellin_transform():
    from sympy import sin, simplify, expand_func, powsimp
    IMT = inverse_mellin_transform

    assert IMT(gamma(s), s, x, (0, oo)) == exp(-x)
    assert IMT(gamma(-s), s, x, (-oo, 0)) == exp(-1/x)
    assert IMT(s/(2*s**2 - 2), s, x, (2, oo)) \
           == (x**2 + 1)*Heaviside(1 - x)/(4*x)

    # test passing "None"
    assert IMT(1/(s**2 - 1), s, x, (-1, None)) \
           == -x*Heaviside(-x + 1)/2 - Heaviside(x - 1)/(2*x)
    assert IMT(1/(s**2 - 1), s, x, (None, 1)) \
           == -x*Heaviside(-x + 1)/2 - Heaviside(x - 1)/(2*x)

    # test expansion of sums
    assert IMT(gamma(s) + gamma(s-1), s, x, (1, oo)) == (x + 1)*exp(-x)/x

    # test factorisation of polys
    assert simplify(expand_func(IMT(1/(s**2 + 1), s, exp(-x),
                                    (None, oo))).rewrite(sin)) \
           == sin(x)*Heaviside(1 - exp(-x))

    # test multiplicative substitution
    a, b = symbols('a b', positive=True)
    assert IMT(b**(-s/a)*factorial(s/a)/s, s, x, (0, oo)) == exp(-b*x**a)
    assert IMT(factorial(a/b + s/b)/(a+ s), s, x, (-a, oo)) == x**a*exp(-x**b)

    def simp_pows(expr): return simplify(powsimp(expr, force=True))

    # Now test the inverses of all direct transforms tested above
    assert IMT(-1/(nu + s), s, x, (-oo, None)) == x**nu*Heaviside(x - 1)
    assert IMT(1/(nu + s), s, x, (None, oo)) == x**nu*Heaviside(1 - x)
    assert IMT(gamma(beta)*gamma(s)/gamma(s + beta), s, x, (0, oo)) \
           == (1 - x)**(beta - 1)*Heaviside(1 - x)
    assert simp_pows(IMT(gamma(beta)*gamma(1-beta-s)/gamma(1-s),
                         s, x, (-oo, None))) \
           == (x - 1)**(beta - 1)*Heaviside(x - 1)
    assert simp_pows(IMT(gamma(s)*gamma(rho-s)/gamma(rho), s, x, (0, None))) \
           == (1/(x + 1))**rho
    # TODO when better combsimp is in place, test abs(1-x)**(-rho)

def test_laplace_transform():
    LT = laplace_transform
    a, b, c, = symbols('a b c', positive=True)
    t = symbols('t')

    # basic tests from wikipedia

    assert LT((t-a)**b*exp(-c*(t-a))*Heaviside(t-a), t, s) \
           == ((s + c)**(-b - 1)*exp(-a*s)*gamma(b + 1), -c, True)
    assert LT(t**a, t, s) == (s**(-a - 1)*gamma(a + 1), 0, True)
    assert LT(Heaviside(t), t, s) == (1/s, 0, True)
    assert LT(Heaviside(t - a), t, s) == (exp(-a*s)/s, 0, True)
    assert LT(1 - exp(-a*t), t, s) == (a/(s*(a + s)), 0, True)

    assert LT((exp(2*t)-1)*exp(-b - t)*Heaviside(t)/2, t, s, noconds=True) \
           == exp(-b)/(s**2 - 1)

    assert LT(exp(t), t, s)[0:2] == (1/(s-1), 1)
    assert LT(exp(2*t), t, s)[0:2] == (1/(s-2), 2)
    assert LT(exp(a*t), t, s)[0:2] == (1/(s-a), a)

    # TODO more basic functions when tables are extended

def test_inverse_laplace_transform():
    from sympy import expand, sinh, cosh, besselj
    ILT = inverse_laplace_transform
    a, b, c, = symbols('a b c', positive=True)
    t = symbols('t')

    def simp_hyp(expr):
        return expand(expand(expr).rewrite(sin))

    # just test inverses of all of the above
    assert ILT(1/s, s, t) == Heaviside(t)
    assert ILT(1/s**2, s, t) == t*Heaviside(t)
    assert ILT(1/s**5, s, t) == t**4*Heaviside(t)/factorial(4)
    assert ILT(exp(-a*s)/s, s, t) == Heaviside(t-a)
    assert ILT(exp(-a*s)/(s+b), s, t) == exp(a*b - b*t)*Heaviside(t - a)
    assert ILT(a/(s**2 + a**2), s, t) == sin(a*t)*Heaviside(t)
    assert ILT(s/(s**2 + a**2), s, t) == cos(a*t)*Heaviside(t)
    # TODO is there a way around simp_hyp?
    assert simp_hyp(ILT(a/(s**2 - a**2), s, t)) == sinh(a*t)*Heaviside(t)
    assert simp_hyp(ILT(s/(s**2 - a**2), s, t)) == cosh(a*t)*Heaviside(t)
    assert ILT(a/((s+b)**2 + a**2), s, t) == exp(-b*t)*sin(a*t)*Heaviside(t)
    assert ILT((s+b)/((s+b)**2 + a**2), s, t) == exp(-b*t)*cos(a*t)*Heaviside(t)
    # TODO sinh/cosh shifted come out a mess. also delayed trig is a mess
    # TODO should this simplify further?
    assert ILT(exp(-a*s)/s**b, s, t) == \
      (-1)**(b + 1)*(a - t)**(b - 1)*Heaviside(t - a)/gamma(b)

    assert ILT(exp(-a*s)/sqrt(1 + s**2), s, t) == \
        Heaviside(t - a)*besselj(0, a - t) # note: besselj(0, x) is even

    # TODO everything from the direct transforms
