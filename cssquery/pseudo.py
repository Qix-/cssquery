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


PSEUDO = {
    'first': _p_first,
    'last': _p_last
}


FUNCTIONS = {
    'nth-child': _f_nth
}
