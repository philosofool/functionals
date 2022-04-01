from collections import namedtuple
from functools import lru_cache
from typing import Callable

@lru_cache()
def nt_builder(name: str, fields) -> namedtuple:
    """Build a named tuple."""
    return namedtuple(name, fields)
    
def sequential_compose(*funcs):
    """Compose function: sequential_compose(f, g, h)(x) == h(g(f(x)))."""
    def compose2(f, g):
        return lambda *a, **kw: g(f(*a, **kw))
    return functools.reduce(compose2, funcs)

def explode_list(L):
    for e in L:
        if hasattr(e, '__iter__') and isinstance(e, str):
            yield from explode_list(e)
        else:
            yield e

# tests
# TODO: move these to a testing file.

def squares(*args):
    return (x**2 for x in args)

assert sequential_compose(squares, sum, lambda x: x == 36)(3, 3, 3, 3)
assert sequential_compose(squares, sum, lambda x: x == 25)(3, 4)

assert list(explode_list([1, 2, 3])) == [1, 2, 3]
assert list(explode_list([1, [2, 3]])) == [1, 2, 3]
assert list(explode_list([1, 2, "three"])) == [1, 2, "three"]
assert list(explode_list([[1, [2]], 3])) == [1, 2, 3]