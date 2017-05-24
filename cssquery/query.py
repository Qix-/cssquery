from __future__ import absolute_import

import functools
import inspect


def _isiterable(obj):
    return hasattr(obj, '__iter__')


def _get_tag(obj):
    if obj is None:
        return None
    if callable(obj.__cq_tag__):
        return obj.__cq_tag__()
    if inspect.isclass(obj):
        return obj.__class__.__name__
    return getattr(obj, '__name__', None)


def _get_children(obj):
    if obj is None:
        return None
    if callable(obj.__cq_children__):
        return obj.__cq_children__()
    if _isiterable(obj):
        return (x for x in obj)
    return None


def _get_id(obj):
    if obj is None:
        return None
    if callable(obj.__cq_id__):
        return obj.__cq_id__()
    return None


def _get_class(obj, k):
    if obj is None:
        return False
    if callable(obj.__cq_class__):
        return obj.__cq_class__(k)
    return bool(getattr(obj, k, False))


def _get_attr(obj, k):
    if obj is None:
        return None
    if callable(obj.__cq_attr__):
        return obj.__cq_attr__(k)
    return getattr(obj, k, None)


class _objset(object):
    def __init__(self):
        self.items = []
        self._ids = set()
        self._hashed = set()

    def add(self, obj):
        if obj and obj.__hash__:
            if obj in self._hashed:
                return
            self._hashed.add(obj)
        else:
            if id(obj) in self._ids:
                return
            self._ids.add(id(obj))

        self.items.append(obj)


COMBINATORS = {
}


def _subquery(selector, obj, results, tagfn, childfn, idfn, classfn, attrfn):
    if not _isiterable(obj):
        obj = [obj]

    if isinstance(selector, csp.Element):
        for o in obj:
            if tagfn(o) is selector.element:
                results.add(o)
        return

    if isinstance(selector, csp.CombinedSelector):
        subresults = _objset()
        for o in obj:
            _subquery(selector.selector, o, subresults, tagfn, childfn, idfn, classfn, attrfn)

        combinatorfn = COMBINATORS.get(selector.combinator)
        if not combinatorfn:
            raise Exception('unsupported combinator: \'{}\''.format(selector.combinator))

        for subresult in subresults.items:



class PrecompiledSelector(object):
    def __init__(self, selector, tagfn=_get_tag, childfn=_get_children, idfn=_get_id, classfn=_get_class, attrfn=_get_attr):
        self._selector = selector
        self._fns = dict(tagfn=tagfn, childfn=childfn, idfn=idfn, classfn=classfn, attrfn=attrfn)

    def query(self, obj):
        result = _objset()

        # because self._selector is actually an array of
        # selectors.
        for selector in self._selector:
            _subquery(selector.parsed_tree, obj, result, **self._fns)

        return result.items


@functools.lru_cache()
def precompile(select_string, tagfn=_get_tag, childfn=_get_children, idfn=_get_id, classfn=_get_class, attrfn=_get_attr):
    import cssselect
    return PrecompiledSelector(cssselect.parse(select_string))


def query(select_string, obj, tagfn=_get_tag, childfn=_get_children, idfn=_get_id, classfn=_get_class, attrfn=_get_attr):
    return precompile(select_string).query(obj)
