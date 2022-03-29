from collections import namedtuple
from functools import lru_cache

@lru_cache()
def nt_builder(name: str, fields) -> namedtuple:
    """Build a named tuple."""
    return namedtuple(name, fields)
    
def compose_function(*funcs) -> Callable:
    """Compose sequential function."""
    def composed(*args, **kwargs):
        for func in funcs:
            try:
                t = func(*t)
            except NameError:
                t = func(*args, *kwargs)
        return t
    return composed

def explode_list(L):
    for e in L:
        if hasattr(e, '__iter__') and isinstance(e, str):
            yield from explode_list(e)
        else:
            yield e