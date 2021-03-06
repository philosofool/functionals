"""Dictionary functionals contains functions that return dictionary manipulating functions.

Functionals take zero or more parameters that specify how to manipulate a dictionary. Their returned 
functions take one or more dictionaries and return a value.

Functionals
-----------
has_keys:
    Tests whether dictionary has the keys in a list.

filter_values:
    Tests whether values in a dictionary satisfy a predicate.

extract_keys:
    Return a dictionary including only certain keys.

drop_keys:
    Return a dictionary excluding certain keys.

map_values:
    Apply a mapping to specified keys, returning the transformed dictionary.

flatten_dictionary:
    Return a dictionary that inherits the key-value pairs of any dictionary-valued key.

"""

from typing import List, Callable, Dict, Any, Union
from functools import singledispatch, lru_cache
from collections import namedtuple
from .utils import nt_builder

FunctionalMap = Dict[Any, Callable]

def has_keys(keys: List, every: bool = True, only: bool = False) -> Callable[[dict], dict]:
    """True if all/only keys are dictionary.
    
    every: bool
        Requires all keys to be in a dictionary.

    only: bool
        Requires all dictionary keys to be in keys.
    
    If both all and only are false, returns True if and only if the dictionary is not
    empty.

    """
    def _func(dict_):
        if every and only:
            has_only = all([k in keys for k in dict_])
            has_all = all([k in dict_.keys() for k in keys])
            return has_all and has_only
        if every:
            return all([k in dict_ for k in keys])
        if only:
            return all([k in keys for k in dict_])
        return bool(dict_)
    return _func


def filter_values(mapping: FunctionalMap):
    """Return True if predicate in mapping is true for all.""" 
    @singledispatch
    def _func(dict_: dict) -> Callable[[Dict[Any, Callable]], dict]:
        return all(mapping[k](dict_[k]) for k in mapping)

    @_func.register
    def _(dict_: tuple):
        return all(mapping[k](getattr(dict_, k)) for k in mapping)
    return _func

def extract_keys(keys: List[str]) -> Callable[[dict], dict]:
    """Returns dictionary whose only keys are keys parameter."""
    @singledispatch
    def _func(dict_: dict) -> dict:
        return {k: v for k, v in dict_.items() if k in keys}

    @_func.register
    def _(dict_: tuple):
        fields = [field for field in dict_._fields if field in keys]
        new_namedtuple = nt_builder('extracted', *fields)
        return new_namedtuple._make(getattr(dict_, f) for f in fields)
    return _func

def add_keys(new_keys: dict) -> Callable[[dict], dict]:
    """Return a dictionary with keys added."""
    @singledispatch
    def _func(dict_: dict) -> dict:
        out = dict_.copy()
        out.update(new_keys)
        return out

    @_func.register(tuple)
    def _(dict_: tuple):
        dict_ = dict_._asdict()
        dict_.update(new_keys)
        new_namedtuple = nt_builder('rekeyed', tuple(dict_.keys()))
        return new_namedtuple._make(**dict_)
    return _func

def drop_keys(keys: List[str]) -> Callable[[dict], dict]:
    """Returns dictionary without keys in keys parameter."""
    @singledispatch
    def _func(dict_: dict) -> dict:
        return {k: v for k, v in dict_.items() if k not in keys}

    @_func.register
    def _(dict_: tuple):
        fields = [field for field in dict_._fields if field not in keys]
        new_namedtuple = nt_builder('dropped', fields)
        return new_namedtuple._make(getattr(dict_, f) for f in fields)
    return _func

def rekey(mapping: Union[Callable, dict]):
    """Change key names in a dictionary.

    Parameters
    ----------
    mapping: 
        Either a dictionary or function. If a dictionary, any key will in an input 
        dictionary will be changed to its value in mapping, if the key exists. If a function,
        the function is applied to each key in the dictionary.

    Examples
    --------
    >>>> rekey(str)({1: 'one'})
    {'1': 'one'}
    >>>> rekey({1: 'one'})({1: 1})
    {'one': 1}
    """ 
    def _func(dict_):
        if isinstance(mapping, dict):
            out = dict_.copy()
            out.update({mapping[k]: v for k, v in mapping.items()})
            drop_keys = [key for key in mapping if key not in mappying.values()]
            return drop_keys([key for key in dict_ if key in drop_keys])(out)
        return {mapping(k): v for k, v in dict_.items()}
    return _func



def map_values(mapping: FunctionalMap):
    """Apply a mapping to each column."""
    @singledispatch
    def _func(dict_: dict) -> dict:
        anon = (lambda k, v: mapping[k](v) if k in mapping else v)
        return {k: anon(k, v) for k, v in dict_.items()}

    @_func.register
    def _(dict_: tuple) -> tuple:
        mapped = {k: mapping[k](getattr(dict_, k)) for k in mapping}
        return dict_._replace(**mapped)
    
    return _func

def flatten_dict(keys=None):
    """Flatten the dictionary, i.e., make each key have a non-dict value,
    adding keys from dict valued keys.

    Parameter
    ---------
    keys: 
        Optional. The keys to be flattened.
    """
    def prefix_key(key, k):
        return str(key) + '__' + str(k)
    def _func(dict_):
        out = {k: v for k, v in dict_.items() if type(v) != dict}
        if keys is None:
            _keys = [key for key in dict_ if key not in out]
        else:
            _keys = keys
        for key in _keys:
            out.update({prefix_key(key, k): v for k, v in dict_[key].items()})
        return out
    return _func

def sequential_func(*functions):
    """Apply functions in order."""
    def _func(*args):
        for function in functions:
            try:
                args = function(*args)
            except TypeError:
                args = function(args)
        return args
    return _func