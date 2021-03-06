module Tag :DeepFrozen
export (Term, makeTerm)

object TermStamp as DeepFrozen:
    to audit(_):
        return true

def TermData :DeepFrozen := any[nullOk, str, int, float, char]

object Term as DeepFrozen:
    to coerce(specimen, ej):
        if (!__auditedBy(TermStamp, specimen)):
            def coerced := specimen._conformTo(Term)
            if (!__auditedBy(TermStamp, coerced)):
                throw.eject(ej, `not a Term: ${M.toQuote(specimen)}`)
        return specimen


object makeTerm as DeepFrozen:
    to asType():
        return Term

    to run(tag :Tag, data :TermData, args :nullOk[List], span):
        if (data != null && args != null):
            throw(`Term $tag can't have both data and children`)

        return object term implements TermStamp, Transparent, Selfless:
            to _uncall():
                return [makeTerm, "run", [tag, data, args, span]]

            to withSpan(newSpan):
                return makeTerm(tag, data, args, newSpan)

            to getTag():
                return tag

            to getData():
                return data

            to getSpan():
                return span

            to getArgs():
                return args

            to withoutArgs():
               return makeTerm(tag, data, [], span)

            to op__cmp(other):
               var tagCmp := tag.op__cmp(other.getTag())
               if (tagCmp != 0):
                   return tagCmp
               if (data != null):
                   if (other.getData() != null):
                       return -1
               else:
                   if (other.getData() == null):
                       return 1
                   def dataCmp := data.op__cmp(other.getData())
                   if (dataCmp != 0):
                       return dataCmp
               return args.op__cmp(other.getArgs())

            # Used for pretty printing. Oughta be cached, but we need a
            # primitive memoizer for that to be DeepFrozen.
            to getHeight():
                var myHeight := 1
                if (args != null):
                    for a in args:
                        def h := a.getHeight()
                        if (h + 1 > myHeight):
                            myHeight := h + 1
                return myHeight

            to _conformTo(guard):
                def x := args != null && args.size() == 0
                if (x && [str, float, int, char].contains(guard)):
                    if (data == null):
                        return tag.getTagName()
                    return data
                else:
                    return term

            to _printOn(out):
                return term.prettyPrintOn(out, false)

            to prettyPrintOn(out, isQuasi :boolean):
                var label := null # should be def w/ later bind
                var reps := null
                var delims := null
                switch (data):
                    match ==null:
                        label := tag.getTagName()
                    match f :float:
                        if (f.isNaN()):
                            label := "%NaN"
                        else if (f.isInfinite()):
                            if (f > 0):
                                label := "%Infinity"
                            else:
                                label := "-%Infinity"
                        else:
                            label := `$data`
                    match s :str:
                        label := s.quote().replace("\n", "\\n")
                    match _:
                        label := M.toQuote(data)

                if (isQuasi):
                    # Escape QL characters.
                    label := label.replace("$", "$$").replace("@", "@@")
                    label := label.replace("`", "``")

                if (label == ".tuple."):
                    if (term.getHeight() <= 1):
                        out.raw_print("[]")
                        return
                    reps := 1
                    delims := ["[", ",", "]"]
                else if (label == ".bag."):
                    if (term.getHeight() <= 1):
                        out.print("{}")
                        return
                    reps := 1
                    delims := ["{", ",", "}"]
                else if (args == null):
                    out.print(label)
                    return
                else if (args.size() == 1 && (args[0].getTag().getTagName() != null)):
                    out.print(label)
                    out.print("(")
                    args[0].prettyPrintOn(out, isQuasi)
                    out.print(")")
                    return
                else if (args.size() == 2 && label == ".attr."):
                    reps := 4
                    delims := ["", ":", ""]
                else:
                    out.print(label)
                    if (term.getHeight() <= 1):
                        # Leaf, so no parens.
                        return
                    reps := label.size() + 1
                    delims := ["(", ",", ")"]
                def [open, sep, close] := delims
                out.print(open)

                if (term.getHeight() == 2):
                    # We only have leaves, so we can probably get away with
                    # printing on a single line.
                    args[0].prettyPrintOn(out, isQuasi)
                    for a in args.slice(1):
                        out.print(sep + " ")
                        a.prettyPrintOn(out, isQuasi)
                    out.print(close)
                else:
                    def sub := out.indent(" " * reps)
                    args[0].prettyPrintOn(sub, isQuasi)
                    for a in args.slice(1):
                        sub.println(sep)
                        a.prettyPrintOn(sub, isQuasi)
                    sub.print(close)
