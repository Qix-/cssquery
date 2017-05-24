from unittest import TestCase

from cssquery.parser import parse, OP


VALID_IDENTS = ['a', 'foobar', 'FooBar', 'hi-there', 'hi_there', '-some-tricky-tag', 'Some------tricky----12345-tag', 'a105-']
VALID_EXPRS = ['is_true', 'y==10', 'len(child.bar) != [1, 2, 3][1]', 'foo == {\'hello\': [1, 2, 3, 4, 5]}']


def _test_pad(*args):
    for i in range(0, 3):
        if len(args) == 1:
            yield '{}{}{}'.format(' ' * i, args[0], ' ' * (i + 1))
        else:
            for next_val in _test_pad(*args[1:]):
                yield '{}{}{}{}'.format(' ' * i, args[0], ' ' * (i + 1), next_val)


class TestParser(TestCase):
    def test_wildcard(self):
        for t in _test_pad('*'):
            self.assertEqual(parse(t), [[(OP.ANY,)]])

    def test_basic_tag(self):
        for tag in VALID_IDENTS:
            for t in _test_pad(tag):
                self.assertEqual(parse(t), [[(OP.TAG, tag)]])

    def test_basic_id(self):
        for i in VALID_IDENTS:
            for t in _test_pad('#' + i):
                self.assertEqual(parse(t), [[(OP.ID, i)]])

    def test_basic_class(self):
        for cls in VALID_IDENTS:
            for t in _test_pad('.' + cls):
                self.assertEqual(parse(t), [[(OP.CLASS, cls)]])

    def test_tag_id(self):
        for tag in VALID_IDENTS:
            for i in VALID_IDENTS:
                for t in _test_pad('{}#{}'.format(tag, i)):
                    self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.ID, i)]])

    def test_multi_class(self):
        for c1 in VALID_IDENTS:
            for c2 in VALID_IDENTS:
                for t in _test_pad('.{}.{}'.format(c1, c2)):
                    self.assertEqual(parse(t), [[(OP.CLASS, c1), (OP.CLASS, c2)]])

    def test_id_class(self):
        for i in VALID_IDENTS:
            for cls in VALID_IDENTS:
                for t in _test_pad('#{}.{}'.format(i, cls)):
                    self.assertEqual(parse(t), [[(OP.ID, i), (OP.CLASS, cls)]])

    def test_multiple_tags(self):
        for tag in VALID_IDENTS:
            for tag2 in VALID_IDENTS:
                for t in _test_pad(tag, tag2):
                    self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.CHILD,), (OP.TAG, tag2)]])

    def test_multiple_selectors(self):
        for tag in VALID_IDENTS:
            for i in VALID_IDENTS:
                for t in _test_pad(tag, '#' + i, ',', '{}#{}'.format(tag, i)):
                    self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.CHILD,), (OP.ID, i)], [(OP.TAG, tag), (OP.ID, i)]])

    def test_evals(self):
        for tag in VALID_IDENTS:
            for ev in VALID_EXPRS:
                for t in _test_pad('{}[{}]'.format(tag, ev)):
                    self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.EVAL, ev)]])

    def test_pseudos(self):
        for tag in VALID_IDENTS:
            for psu in VALID_IDENTS:
                for t in _test_pad('{}:{}'.format(tag, psu)):
                    self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.PSEUDO, psu)]])

    def test_functions(self):
        for tag in VALID_IDENTS:
            for fn_name in VALID_IDENTS:
                # use re-use valid expressions here
                for fn_args in VALID_EXPRS:
                    for t in _test_pad('{}:{}({})'.format(tag, fn_name, fn_args)):
                        self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.FN, (fn_name, fn_args))]])

    def test_direct_child(self):
        for tag in VALID_IDENTS:
            for t in _test_pad(tag, '>', tag):
                self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.CHILD_DIRECT,), (OP.TAG, tag)]])

    def test_direct_sibling(self):
        for tag in VALID_IDENTS:
            for t in _test_pad(tag, '+', tag):
                self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.SIBLING_DIRECT,), (OP.TAG, tag)]])

    def test_sibling(self):
        for tag in VALID_IDENTS:
            for t in _test_pad(tag, '~', tag):
                self.assertEqual(parse(t), [[(OP.TAG, tag), (OP.SIBLING,), (OP.TAG, tag)]])

    def test_complex(self):
        self.assertEqual(parse('foo#bar.mcgee:blah(x*(4+5)+n)'),
            [[(OP.TAG, 'foo'), (OP.ID, 'bar'), (OP.CLASS, 'mcgee'), (OP.FN, ('blah', 'x*(4+5)+n'))]])
        self.assertEqual(parse(':not(disconnected) .node.function #foobar:nth-child(10) ~ struct.pod, struct.pod[len(children) > 10]'),
            [[(OP.FN, ('not', 'disconnected')), (OP.CHILD,), (OP.CLASS, 'node'), (OP.CLASS, 'function'), (OP.CHILD,),
              (OP.ID, 'foobar'), (OP.FN, ('nth-child', '10')), (OP.SIBLING,), (OP.TAG, 'struct'), (OP.CLASS, 'pod')],
             [(OP.TAG, 'struct'), (OP.CLASS, 'pod'), (OP.EVAL, 'len(children) > 10')]])
