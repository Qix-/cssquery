from __future__ import absolute_import

import functools
import inspect

from .error import CssQueryError
from .parser import parse, OP


def _isiterable(obj):
    return hasattr(obj, '__iter__')


def _get_tag(obj):
    if obj is None:
        return None
    if callable(getattr(obj, '__cq_tag__', None)):
        return obj.__cq_tag__()
    if inspect.isclass(obj):
        return obj.__class__.__name__
    return getattr(obj, '__name__', None)


def _get_children(obj):
    if obj is None:
        return None
    if callable(getattr(obj, '__cq_children__', None)):
        return obj.__cq_children__()
    if _isiterable(obj):
        return (x for x in obj)
    return None


def _get_id(obj):
    if obj is None:
        return None
    if callable(getattr(obj, '__cq_id__', None)):
        return obj.__cq_id__()
    return None


def _get_class(obj, k):
    if obj is None:
        return False
    if callable(getattr(obj, '__cq_class__', None)):
        return obj.__cq_class__(k)
    return bool(getattr(obj, k, False))


def _get_attr(obj, k):
    if obj is None:
        return None
    if callable(getattr(obj, '__cq_attr__', None)):
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


def _all_children(obj, childfn):
    yield obj
    for child in childfn(obj) or ():
        yield child
        for subchild in _all_children(child, childfn):
            yield subchild


def _transform(step, obj, fns):
    op = step[0]
    value = step[1] if len(step) > 1 else None

    if op == OP.CHILD:
        for child in _all_children(obj, fns['childfn']):
            yield child
    elif op == OP.TAG:
        for child in fns['childfn'](obj) or ():
            if fns['tagfn'](child) == value:
                yield child
    else:
        raise CssQueryError('bad operation: {}'.format(step))


def _subquery(selector, obj, result, fns):
    for step in selector:
        obj = _transform(step, obj, fns)

    for child in obj:
        result.add(child)


class PrecompiledSelector(object):
    def __init__(self, selector, tagfn=_get_tag, childfn=_get_children, idfn=_get_id, classfn=_get_class, attrfn=_get_attr):
        self._selector = selector
        self._fns = dict(tagfn=tagfn, childfn=childfn, idfn=idfn, classfn=classfn, attrfn=attrfn)

    def query(self, objs):
        result = _objset()

        # because self._selector is actually an array of
        # selectors.
        for obj in objs:
            for selector in self._selector:
                _subquery(selector, obj, result, self._fns)

        return result.items


@functools.lru_cache()
def precompile(select_string):
    return PrecompiledSelector(parse(select_string))


def query(select_string, objs, tagfn=_get_tag, childfn=_get_children, idfn=_get_id, classfn=_get_class, attrfn=_get_attr):
    if not _isiterable(objs):
        raise CssQueryError('objs must be an iterable of objects: {}'.format(objs))
    return precompile(select_string).query((x for x in objs))
