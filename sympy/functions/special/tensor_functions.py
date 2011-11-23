import operator
from sympy.core.compatibility import reduce
from sympy.core.function import Function
from sympy.core import sympify, S, Integer
from sympy.core.mul import prod

###############################################################################
###################### Kronecker Delta, Levi-Civita etc. ######################
###############################################################################

def Eijk(*args, **kwargs):
    """
    Represent the Levi-Civita symbol.

    This is just compatibility wrapper to LeviCivita().
    """
    return LeviCivita(*args, **kwargs)

def eval_levicivita(*args):
    """Evaluate Levi-Civita symbol."""
    from sympy import factorial
    n = len(args)
    return prod(
        prod(args[j] - args[i] for j in xrange(i + 1, n))
        / factorial(i) for i in xrange(n))
    # converting factorial(i) to int is slightly faster

class LeviCivita(Function):
    """Represent the Levi-Civita symbol.

    For even permutations of indices it returns 1, for odd permutations -1, and
    for everything else (a repeated index) it returns 0.

    Thus it represents an alternating pseudotensor.

    >>> from sympy import LeviCivita, symbols
    >>> LeviCivita(1,2,3)
    1
    >>> LeviCivita(1,3,2)
    -1
    >>> LeviCivita(1,2,2)
    0
    >>> i,j,k = symbols('i j k')
    >>> LeviCivita(i,j,k)
    LeviCivita(i, j, k)
    >>> LeviCivita(i,j,i)
    0
    """
    @classmethod
    def eval(cls, *args):
        if all(isinstance(a, (int, Integer)) for a in args):
            return eval_levicivita(*args)
        if len(set(args)) < len(args):
            return S.Zero

    def doit(self):
        return eval_levicivita(*self.args)

class KroneckerDelta(Function):
    """The discrete, or Kronecker, delta function.

    A function that takes in two integers i and j. It returns 0 if i and j are
    not equal or it returns 1 if i and j are equal.

    Parameters
    ==========
    i : Number, Symbol
        The first index of the delta function.
    j : Number, Symbol
        The second index of the delta function.

    Examples
    ========

    A simple example with integer indices::

        >>> from sympy.physics.quantum import KroneckerDelta
        >>> KroneckerDelta(1,2)
        0
        >>> KroneckerDelta(3,3)
        1

    Symbolic indices::

        >>> from sympy import symbols
        >>> i, j, k = symbols('i j k')
        >>> KroneckerDelta(i, j)
        d(i,j)
        >>> KroneckerDelta(i, i)
        1
        >>> KroneckerDelta(i, i+1)
        0
        >>> KroneckerDelta(i, i+1+k)
        d(i,i + k + 1)

    References
    ==========

    http://en.wikipedia.org/wiki/Kronecker_delta
    """

    nargs = 2
    is_commutative=True

    @classmethod
    def eval(cls, i, j):
        """
        Evaluates the discrete delta function.

        >>> from sympy import symbols
        >>> from sympy.physics.secondquant import KroneckerDelta
        >>> i, j, k = symbols('i,j,k')
        >>> KroneckerDelta(i, j)
        KroneckerDelta(i, j)
        >>> KroneckerDelta(i, i)
        1
        >>> KroneckerDelta(i, i+1)
        0
        >>> KroneckerDelta(i, i+1+k)
        KroneckerDelta(i, i + k + 1)

        # indirect doctest

        """
        if i > j:
            return cls(j,i)
        diff = i-j
        if diff == 0:
            return S.One
        elif diff.is_number:
            return S.Zero

        if i.assumptions0.get("below_fermi") and j.assumptions0.get("above_fermi"):
            return S.Zero
        if j.assumptions0.get("below_fermi") and i.assumptions0.get("above_fermi"):
            return S.Zero
    @property
    def is_above_fermi(self):
        """
        True if Delta can be non-zero above fermi

        >>> from sympy.physics.secondquant import KroneckerDelta
        >>> from sympy import Symbol
        >>> a = Symbol('a',above_fermi=True)
        >>> i = Symbol('i',below_fermi=True)
        >>> p = Symbol('p')
        >>> q = Symbol('q')
        >>> KroneckerDelta(p,a).is_above_fermi
        True
        >>> KroneckerDelta(p,i).is_above_fermi
        False
        >>> KroneckerDelta(p,q).is_above_fermi
        True

        """
        if self.args[0].assumptions0.get("below_fermi"):
            return False
        if self.args[1].assumptions0.get("below_fermi"):
            return False
        return True

    @property
    def is_below_fermi(self):
        """
        True if Delta can be non-zero below fermi

        >>> from sympy.physics.secondquant import KroneckerDelta
        >>> from sympy import Symbol
        >>> a = Symbol('a',above_fermi=True)
        >>> i = Symbol('i',below_fermi=True)
        >>> p = Symbol('p')
        >>> q = Symbol('q')
        >>> KroneckerDelta(p,a).is_below_fermi
        False
        >>> KroneckerDelta(p,i).is_below_fermi
        True
        >>> KroneckerDelta(p,q).is_below_fermi
        True

        """
        if self.args[0].assumptions0.get("above_fermi"):
            return False
        if self.args[1].assumptions0.get("above_fermi"):
            return False
        return True

    @property
    def is_only_above_fermi(self):
        """
        True if Delta is restricted to above fermi

        >>> from sympy.physics.secondquant import KroneckerDelta
        >>> from sympy import Symbol
        >>> a = Symbol('a',above_fermi=True)
        >>> i = Symbol('i',below_fermi=True)
        >>> p = Symbol('p')
        >>> q = Symbol('q')
        >>> KroneckerDelta(p,a).is_only_above_fermi
        True
        >>> KroneckerDelta(p,q).is_only_above_fermi
        False
        >>> KroneckerDelta(p,i).is_only_above_fermi
        False

        """
        return ( self.args[0].assumptions0.get("above_fermi")
                or
                self.args[1].assumptions0.get("above_fermi")
                ) or False

    @property
    def is_only_below_fermi(self):
        """
        True if Delta is restricted to below fermi

        >>> from sympy.physics.secondquant import KroneckerDelta
        >>> from sympy import Symbol
        >>> a = Symbol('a',above_fermi=True)
        >>> i = Symbol('i',below_fermi=True)
        >>> p = Symbol('p')
        >>> q = Symbol('q')
        >>> KroneckerDelta(p,i).is_only_below_fermi
        True
        >>> KroneckerDelta(p,q).is_only_below_fermi
        False
        >>> KroneckerDelta(p,a).is_only_below_fermi
        False

        """
        return ( self.args[0].assumptions0.get("below_fermi")
                or
                self.args[1].assumptions0.get("below_fermi")
                ) or False

    @property
    def indices_contain_equal_information(self):
        """
        Returns True if indices are either both above or below fermi.

        Example:

        >>> from sympy.physics.secondquant import KroneckerDelta
        >>> from sympy import Symbol
        >>> a = Symbol('a',above_fermi=True)
        >>> i = Symbol('i',below_fermi=True)
        >>> p = Symbol('p')
        >>> q = Symbol('q')
        >>> KroneckerDelta(p, q).indices_contain_equal_information
        True
        >>> KroneckerDelta(p, q+1).indices_contain_equal_information
        True
        >>> KroneckerDelta(i, p).indices_contain_equal_information
        False

        """
        if (self.args[0].assumptions0.get("below_fermi") and
                self.args[1].assumptions0.get("below_fermi")):
            return True
        if (self.args[0].assumptions0.get("above_fermi")
                and self.args[1].assumptions0.get("above_fermi")):
            return True

        # if both indices are general we are True, else false
        return self.is_below_fermi and self.is_above_fermi


    @property
    def preferred_index(self):
        """
        Returns the index which is preferred to keep in the final expression.

        The preferred index is the index with more information regarding fermi
        level.  If indices contain same information, 'a' is preferred before
        'b'.

        >>> from sympy.physics.secondquant import KroneckerDelta
        >>> from sympy import Symbol
        >>> a = Symbol('a',above_fermi=True)
        >>> i = Symbol('i',below_fermi=True)
        >>> j = Symbol('j',below_fermi=True)
        >>> p = Symbol('p')
        >>> KroneckerDelta(p,i).preferred_index
        i
        >>> KroneckerDelta(p,a).preferred_index
        a
        >>> KroneckerDelta(i,j).preferred_index
        i

        """
        if self._get_preferred_index():
            return self.args[1]
        else:
            return self.args[0]

    @property
    def killable_index(self):
        """
        Returns the index which is preferred to substitute in the final expression.

        The index to substitute is the index with less information regarding fermi
        level.  If indices contain same information, 'a' is preferred before
        'b'.

        >>> from sympy.physics.secondquant import KroneckerDelta
        >>> from sympy import Symbol
        >>> a = Symbol('a',above_fermi=True)
        >>> i = Symbol('i',below_fermi=True)
        >>> j = Symbol('j',below_fermi=True)
        >>> p = Symbol('p')
        >>> KroneckerDelta(p,i).killable_index
        p
        >>> KroneckerDelta(p,a).killable_index
        p
        >>> KroneckerDelta(i,j).killable_index
        j

        """
        if self._get_preferred_index():
            return self.args[0]
        else:
            return self.args[1]

    def _get_preferred_index(self):
        """
        Returns the index which is preferred to keep in the final expression.

        The preferred index is the index with more information regarding fermi
        level.  If indices contain same information, index 0 is returned.
        """
        if not self.is_above_fermi:
            if self.args[0].assumptions0.get("below_fermi"):
                return 0
            else:
                return 1
        elif not self.is_below_fermi:
            if self.args[0].assumptions0.get("above_fermi"):
                return 0
            else:
                return 1
        else:
            return 0

    def _dagger_(self):
        return self

    def _eval_dagger(self):
        return self

    def _latex_(self,printer):
        return "\\delta_{%s%s}"% (self.args[0].name,self.args[1].name)

    def _sympyrepr(self, printer, *args):
        return "%s(%s,%s)"% (self.__class__.__name__, self.args[0],\
        self.args[1])

    def _sympystr(self, printer, *args):
        return 'd(%s,%s)'% (self.args[0],self.args[1])

    def _pretty(self, printer, *args):
        pform = printer._print(self.args[0], *args)
        pform = prettyForm(*pform.right((prettyForm(','))))
        pform = prettyForm(*pform.right((printer._print(self.args[1], *args))))
        a = stringPict(u'\u03b4')
        b = pform
        top = stringPict(*b.left(' '*a.width()))
        bot = stringPict(*a.right(' '*b.width()))
        return prettyForm(binding=prettyForm.POW, *bot.below(top))

    def _latex(self, printer, *args):
        i = printer._print(self.args[0], *args)
        j = printer._print(self.args[1], *args)
        return '\\delta_{%s %s}' % (i,j)

