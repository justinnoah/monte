from monte.runtime.base import MonteObject, throw
from monte.runtime.data import String, bwrap, true
from monte.runtime.guards.base import deepFrozenGuard
from monte.runtime.guards.data import booleanGuard

class Audition(MonteObject):
    _m_fqn = "Audition"
    def __init__(self, fqn, expr, bindings, obj, outerNames):
        self.expr = expr
        self.bindings = bindings
        self.approvers = []
        self.obj = obj
        self.fqn = fqn
        self._active = True
        self.outerNames = outerNames

    def ask(self, auditor):
        if not self._active:
            raise RuntimeError("audition is out of scope")
        #XXX caching of audit results
        result = booleanGuard.coerce(auditor.audit(self), throw)
        if result is true:
            self.approvers.append(auditor)

    def getObjectExpr(self):
        return self.expr

    def getGuard(self, name):
        if not isinstance(name, String):
            raise RuntimeError("%r is not a string" % (name,))
        if name.s not in self.bindings:
            raise RuntimeError('"%s" is not a free variable in %s' %
                               (name.s, str(self.obj)))
        return self.bindings[name.s]

    def getFQN(self):
        return self.fqn

    def getOuterNames(self):
        return self.outerNames

class AuditChecker(MonteObject):
    _m_fqn = "__auditedBy"
    _m_auditorStamps = (deepFrozenGuard,)
    def run(self, auditor, specimen):
        return bwrap(auditor in getattr(specimen, "_m_auditorStamps", ()))


auditedBy = AuditChecker()
