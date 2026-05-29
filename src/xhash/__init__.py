#!/usr/bin/env python3
"""
xhash initialization module.

Exposes the primary hashing APIs, internal libraries, and alphabet utilities.
"""

from .xhash512 import xhash512, xhash256, xhash128, xhash64, xhash_dyna
from .xbase64 import XBase64
from . import xhashlib

__pname__ = "xhash"
__author__ = "Fyllus(Geliardi D. Oliveira)"
__version__ = "0.4.0-stable"

__all__ = [
    'xhash512',
    'xhash256',
    'xhash128',
    'xhash64',
    'xhash_dyna',
    'XBase64',
    'xhashlib'
]