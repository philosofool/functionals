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