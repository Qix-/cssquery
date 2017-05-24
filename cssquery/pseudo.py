def _p_first(obj):
    yield next(obj)


def _p_last(obj):
    for x in obj:
        pass
    yield x


def _f_nth(obj, args):
    n = int(args)
    if n >= 0:
        i = 0
        for x in obj:
            if i == n:
                yield x
                break
            i += 1


def _f_attr(obj, args):
    for o in obj:
        if type(o) is dict:
            v = o.get(args, None)
        else:
            v = getattr(o, args, None)
        if v is not None:
            yield v


PSEUDO = {
    'first': _p_first,
    'last': _p_last
}


FUNCTIONS = {
    'nth-child': _f_nth,
    'attr': _f_attr
}
