from monte.runtime.base import MonteObject, toString, toQuote
from monte.runtime.data import String
from monte.runtime.guards.base import deepFrozenGuard

class M(MonteObject):
    _m_fqn = "M"
    _m_auditorStamps = (deepFrozenGuard,)
    def call(self, obj, verb, arglist):
        return getattr(obj, verb)(*arglist)

    def callWithPair(self, obj, (verb, arglist)):
        #XXX typecheck
        return getattr(obj, verb.s)(*arglist.l)

    def send(self, obj, verb, arglist):
        raise NotImplementedError()

    def sendOnly(self, obj, verb, arglist):
        raise NotImplementedError()

    def toString(self, obj):
        # XXX use TextWriter.print
        return String(toString(obj))

    def toQuote(self, obj):
        return String(toQuote(obj))


theM = M()
