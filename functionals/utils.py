from collections import namedtuple
from functools import lru_cache

@lru_cache()
def nt_builder(name: str, fields) -> namedtuple:
    """Build a named tuple."""
    return namedtuple(name, *fields)
    
