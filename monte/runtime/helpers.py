"""
Objects used by Monte syntax expansions.
"""
from monte.runtime.base import MonteObject, ejector, throw
from monte.runtime.data import true, false, null, String, Integer, bwrap
from monte.runtime.equalizer import equalizer
from monte.runtime.flow import MonteIterator
from monte.runtime.guards.base import deepFrozenGuard, deepFrozenFunc
from monte.runtime.ref import UnconnectedRef
from monte.runtime.tables import ConstList, FlexList, ConstMap, FlexMap, mapMaker

@deepFrozenFunc
def validateFor(flag):
    if not flag:
        raise RuntimeError("For-loop body isn't valid after for-loop exits.")

@deepFrozenFunc
def accumulateList(coll, obj):
    it = coll._makeIterator()
    skip = ejector("listcomp_skip")
    ej = ejector("iteration")
    acc = []
    try:
        while True:
            try:
                key, item = it.next(ej)
                acc.append(obj.run(key, item, skip))
            except skip._m_type:
                continue
    except ej._m_type:
        pass
    finally:
        ej.disable()

    return ConstList(acc)

@deepFrozenFunc
def accumulateMap(coll, obj):
    return mapMaker.fromPairs(accumulateList(coll, obj))

@deepFrozenFunc
def iterWhile(f):
    return MonteIterator((null, v) for v in iter(f, false))


class Comparer(MonteObject):
    _m_fqn = "__comparer"
    _m_auditorStamps = (deepFrozenGuard,)

    def greaterThan(self, left, right):
        return left.op__cmp(right).aboveZero()

    def geq(self, left, right):
        return left.op__cmp(right).atLeastZero()

    def lessThan(self, left, right):
        return left.op__cmp(right).belowZero()

    def leq(self, left, right):
        return left.op__cmp(right).atMostZero()

    def asBigAs(self, left, right):
        return left.op__cmp(right).isZero()

comparer = Comparer()


class MakeVerbFacet(MonteObject):
    _m_fqn = "__makeVerbFacet$verbFacet"
    _m_auditorStamps = (deepFrozenGuard,)
    def curryCall(self, obj, verb):
        if not isinstance(verb, String):
            raise RuntimeError("%r is not a string" % (verb,))
        def facet(*a):
            return getattr(obj, verb.s)(*a)
        return facet

makeVerbFacet = MakeVerbFacet()


@deepFrozenFunc
def matchSame(expected):
    def sameMatcher(specimen, ej):
        if equalizer.sameEver(specimen, expected) is true:
            return expected
        else:
            ej("%r is not %r" % (specimen, expected))
    return sameMatcher

@deepFrozenFunc
def switchFailed(specimen, *failures):
    raise RuntimeError("%s did not match any option: [%s]" % (
        specimen,
        " ".join(str(f) for f in failures)))


_absent = object()
@deepFrozenFunc
def suchThat(x, y=_absent):
    if y is _absent:
        # 1-arg invocation.
        def suchThatMatcher(specimen, ejector):
            if not x:
                ejector("such-that expression was false")
        return suchThatMatcher
    else:
        return ConstList([x, None])

@deepFrozenFunc
def extract(x, instead=_absent):
    if instead is _absent:
        # 1-arg invocation.
        def extractor(specimen, ejector):
            return [specimen.fetch(x, lambda: ejector), specimen.without(x)]
        return extractor
    else:
        def extractor(specimen, ejector):
            if not isinstance(specimen, (ConstMap, FlexMap)):
                raise RuntimeError("%r is not a map" % (specimen,))
            value = specimen.d.get(x, _absent)
            if value is _absent:
                value = ConstList([instead(), specimen])
            return [value, specimen.without(x)]
        return extractor


class Empty:
    _m_fqn = "Empty"
    _m_auditorStamps = (deepFrozenGuard,)
    def coerce(self, specimen, ej):
        if specimen.size() == Integer(0):
            return specimen
        else:
            throw.eject(ej, "Not empty: %s" % specimen)

@deepFrozenFunc
def splitList(cut):
    if not isinstance(cut, Integer):
        raise RuntimeError("%r is not an integer" % (cut,))
    cut = cut.n
    def listSplitter(specimen, ej):
        if not isinstance(specimen, (ConstList, FlexList)):
            raise RuntimeError("%r is not a list" % (specimen,))
        if len(specimen.l) < cut:
            throw.eject(
                ej, "A %s size list doesn't match a >= %s size list pattern"
                    % (len(specimen), cut))
        vals = list(specimen.l[:cut])
        vals.append(ConstList(specimen.l[cut:]))
        return ConstList(vals)
    return listSplitter


class BooleanFlow(MonteObject):
    _m_fqn = "__booleanFlow"
    _m_auditorStamps = (deepFrozenGuard,)
    def __init__(self, vat):
        self.vat = vat

    def broken(self):
        return UnconnectedRef("boolean flow expression failed", self.vat)

    def failureList(self, size):
        if not isinstance(size, Integer):
            raise RuntimeError("%r is not an integer" % (size,))
        return ConstList([false] + [self.broken()] * size.n)

@deepFrozenFunc
def makeViaBinder(resolver, guard):
    def bindit(specimen, ej):
        if guard is null:
            resolver.resolve(specimen)
        else:
            resolver.resolve(guard.coerce(specimen, ej))
    return bindit
