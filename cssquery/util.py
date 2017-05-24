# I know I could use Python's enum package,
# but I don't necessarily like it and think this
# ponyfill does it better.


# http://stackoverflow.com/a/1695250/510036
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    t = type('Enum', (), enums)
    setattr(t, 'values', lambda: enums.values())
    return t
