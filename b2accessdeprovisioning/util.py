from __future__ import absolute_import
"""Returns the value blah blah or None"""

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct