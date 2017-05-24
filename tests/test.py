import sys
from unittest import TestCase

from cssquery import precompile, query

sys.setrecursionlimit(10**6)


class Tag(object):
    def __init__(self, tag):
        self._tag = tag

    def __cq_tag__(self):
        return self._tag

    def __cq_children__(self):
        return getattr(self, 'children', None)

    def __cq_id__(self):
        return self.id

    def __cq_class__(self, cls):
        return bool(getattr(self, cls, False))


class TestCssQuery(TestCase):
    def test_same_object(self):
        test = Tag('foo')
        self.assertEqual(query('foo', [test]), [test])

    def test_same_object_precomp(self):
        test = Tag('foo')
        sel = precompile('foo')
        self.assertEqual(sel.query([test]), [test])

    def test_child_object(self):
        test = Tag('foo')
        bar = Tag('bar')
        test.children = [bar]
        self.assertEqual(query('foo bar', [test]), [bar])

    def test_child_object_precomp(self):
        test = Tag('foo')
        bar = Tag('bar')
        test.children = [bar]
        sel = precompile('foo bar')
        self.assertEqual(sel.query([test]), [bar])

    def test_simple_obj(self):
        qix = {'qix': 42, 'enabled': True}
        self.assertEqual(query('.enabled', [{'foo': 'bar', 'qux': qix, 'baz': {'enabled': False}}]), [qix])
