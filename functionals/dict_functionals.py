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
from typing import List, Callable, Dict, Any

FunctionalMap = Dict[Any, Callable]

def has_keys(keys: List, every: bool = True, only: bool = True) -> Callable[[dict], dict]:
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
            has_all = all([k in keys for k in dict_])
            has_only = all([k in dict_.keys() for k in keys])
            return has_all and has_only
        if every:
            return all([k in dict_ for k in keys])
        if only:
            return all([k in keys for k in dict_])
        return bool(dict_)
    return _func

def filter_values(mapping: FunctionalMap):
    """Return True if predicate in mapping is true for all.""" 
    def _func(dict_: dict) -> Callable[[Dict[Any, Callable]], dict]:
        return all(mapping[k](v) for k, v in dict_.items() if k in mapping)
    return _func

def extract_keys(keys: List[str]) -> Callable[[dict], dict]:
    """Returns dictionary whose only keys are keys parameter."""
    def _func(dict_: dict) -> dict:
        return {k: v for k, v in dict_.items() if k in keys}
    return _func

def drop_keys(keys: List[str]) -> Callable[[dict], dict]:
    """Returns dictionary without keys in keys parameter."""
    def _func(dict_: dict) -> dict:
        return {k: v for k, v in dict_.items() if k not in keys}
    return _func

def map_values(mapping: FunctionalMap):
    """Apply a mapping to each column."""
    def _func(dict_: dict) -> dict:
        anon = (lambda k, v: mapping[k](v) if k in mapping else v)
        return {k: anon(k, v) for k, v in dict_.items()}
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

assert flatten_dict(keys=['d'])({"a": 1, 'd': {"b":1, 'c': 1}}) == {'a': 1, 'd__b': 1, 'd__c': 1}

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