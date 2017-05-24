import flexicon

from .util import enum
from .error import CssQueryError


OP = enum(
    'ANY',

    'TAG',
    'CLASS',
    'ID',
    'EVAL',
    'PSEUDO',
    'FN',

    'CHILD',
    'CHILD_DIRECT',
    'SIBLING',
    'SIBLING_DIRECT'
)


class Token(object):
    def __init__(self, line, column, name, value=None):
        self.line = line
        self.column = column
        self.name = name
        self.value = value


def _process_token(pair, lexer):
    return Token(lexer.row, lexer.col, *pair)


SELECTOR_SYNTAX = flexicon.Lexer(_process_token).simple(
    (r'[ \t\r\n]+', lambda: ('WS',)),

    (r'\,', lambda: ('COMMA',)),

    (r'\*', lambda: ('STAR',)),
    (r'\.', lambda: ('DOT',)),
    (r'\#', lambda: ('SHARP',)),  # because 'hash', 'pound' and 'number' all suck

    (r'\+', lambda: ('PLUS',)),
    (r'\>', lambda: ('GT',)),
    (r'\~', lambda: ('TILDE',)),

    (r'\:', lambda: ('COLON',)),

    (r'([a-zA-Z_\-][a-zA-Z0-9_\-]*)', lambda val: ('IDENT', val)),

    # https://stackoverflow.com/a/26386070/510036
    (r'\[((?>[^\[\]]+|(?R))*)\]', lambda expr: ('EVAL', expr)),
    (r'\(((?>[^()]+|(?R))*)\)', lambda args: ('FNARGS', args)),
)


class TokenIterator(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.id = 0
        self.length = len(tokens)

    def next(self):
        self.id += 1
        return self.token

    @property
    def token(self):
        return self.tokens[self.id] if self.id < self.length else None

    @property
    def name(self):
        return self.token.name if self.id < self.length else None

    @property
    def value(self):
        return self.token.value if self.id < self.length else None

    @property
    def line(self):
        return self.token.line if self.id < self.length else None

    @property
    def column(self):
        return self.token.column if self.id < self.length else None

    def peek(self):
        return self.tokens[self.id + 1] if (self.id + 1) < self.length else None

    def expect(self, name):
        self.next()
        if self.name is not name:
            self.unexpected()
        return self

    def unexpected(self):
        val_fmt = ' ({})'.format(self.value) if self.value is not None else ''
        tkn_fmt = 'token {}'.format(self.name) if self.name is not None else 'EOF'
        err = CssQueryError('unexpected {}{}'.format(tkn_fmt, val_fmt))
        err.line = self.line
        err.column = self.column
        raise err

    def burn(self, name):
        while self.name is name:
            self.next()


def parse_selector(itr, terminator, selectors=None):
    if selectors is None:
        selectors = [(OP.CHILD,)]

    itr.burn('WS')

    pushed_child = True
    while itr.name and itr.name is not terminator:
        if itr.name is 'WS':
            itr.burn('WS')
            if itr.token:
                selectors.append((OP.CHILD,))
                pushed_child = True
            continue
        elif itr.name is 'PLUS':
            if pushed_child:
                selectors.pop()
                pushed_child = False
            selectors.append((OP.SIBLING_DIRECT,))
            itr.next()
            itr.burn('WS')
            continue
        elif itr.name is 'GT':
            if pushed_child:
                selectors.pop()
                pushed_child = False
            selectors.append((OP.CHILD_DIRECT,))
            itr.next()
            itr.burn('WS')
            continue
        elif itr.name is 'TILDE':
            if pushed_child:
                selectors.pop()
                pushed_child = False
            selectors.append((OP.SIBLING,))
            itr.next()
            itr.burn('WS')
            continue
        elif itr.name is 'STAR':
            selectors.append((OP.ANY,))
        elif itr.name is 'IDENT':
            selectors.append((OP.TAG, itr.value))
        elif itr.name is 'SHARP':
            itr.expect('IDENT')
            selectors.append((OP.ID, itr.value))
        elif itr.name is 'DOT':
            itr.expect('IDENT')
            selectors.append((OP.CLASS, itr.value))
        elif itr.name is 'EVAL':
            selectors.append((OP.EVAL, itr.value))
        elif itr.name is 'COLON':
            itr.expect('IDENT')
            if itr.peek().name is 'FNARGS':
                selectors.append((OP.FN, (itr.value, itr.next().value)))
            else:
                selectors.append((OP.PSEUDO, itr.value))
        else:
            itr.unexpected()

        pushed_child = False
        itr.next()

    if pushed_child:
        selectors.pop()

    return selectors if len(selectors) > 1 else ()


def parse(source):
    try:
        tokens = SELECTOR_SYNTAX.lex(source)
    except flexicon.FlexiconError as e:
        raise CssQueryError(str(e))

    itr = TokenIterator(tokens)

    selectors = []
    while itr.token is not None:
        selectors.append(parse_selector(itr, 'COMMA'))
        itr.burn('WS')
        if itr.token:
            if itr.token.name is not 'COMMA':
                itr.unexpected()
            itr.next()

    return selectors
